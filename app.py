from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from sqlalchemy import create_engine, String, DateTime, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'change-me')

ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm'}
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Database setup (PostgreSQL via SQLAlchemy)
# Normalize and ensure psycopg v3 driver is used
database_url = os.getenv('DATABASE_URL', '').replace('postgres://', 'postgresql://')
if database_url.startswith('postgresql://') and '+psycopg' not in database_url:
    database_url = database_url.replace('postgresql://', 'postgresql+psycopg://', 1)
if not database_url:
    raise RuntimeError('DATABASE_URL is not set')

engine = create_engine(database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

class Video(Base):
    __tablename__ = 'videos'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    public_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    url: Mapped[str] = mapped_column(String(1024))
    title: Mapped[str] = mapped_column(String(255), default='Uploaded Video')
    description: Mapped[str] = mapped_column(String(1000), default='')
    category: Mapped[str] = mapped_column(String(50), default='coding')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# Ensure columns exist when deploying without migrations (PostgreSQL)
with engine.begin() as conn:
    try:
        conn.execute(text("""
            ALTER TABLE videos
            ADD COLUMN IF NOT EXISTS title varchar(255) DEFAULT 'Uploaded Video';
        """))
        conn.execute(text("""
            ALTER TABLE videos
            ADD COLUMN IF NOT EXISTS description varchar(1000) DEFAULT '';
        """))
    except Exception:
        # Non-fatal; table may not exist yet or DB is not ready
        pass

class Image(Base):
    __tablename__ = 'images'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    public_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    url: Mapped[str] = mapped_column(String(1024))
    title: Mapped[str] = mapped_column(String(255), default='Photo')
    description: Mapped[str] = mapped_column(String(1000), default='')
    category: Mapped[str] = mapped_column(String(50), default='work')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# Cloudinary configuration
cloudinary_url = os.getenv('CLOUDINARY_URL')
if not cloudinary_url:
    # Allow app to start without Cloudinary locally, but uploads will fail
    cloudinary_url = ''
cloudinary.config(cloudinary_url=cloudinary_url)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Simple admin auth configuration
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME') or 'admin'
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD') or 'changeme'

def is_admin_logged_in() -> bool:
    return session.get('is_admin') is True

def login_required(view_func):
    from functools import wraps
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not is_admin_logged_in():
            flash('Please log in to perform this action.')
            return redirect(url_for('login', next=request.path))
        return view_func(*args, **kwargs)
    return wrapped_view

@app.context_processor
def inject_is_admin():
    return { 'is_admin': is_admin_logged_in() }

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/portfolio')
def portfolio():
    with SessionLocal() as db:
        videos = db.query(Video).order_by(Video.created_at.desc()).all()
        images = db.query(Image).order_by(Image.created_at.desc()).all()
    return render_template("portfolio.html", videos=videos, images=images)

@app.route('/contact')
def contact():
    return render_template("contact.html")

ALLOWED_CATEGORIES = {'coding', 'hairdressing'}

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if not os.getenv('CLOUDINARY_URL'):
        flash('Cloudinary is not configured. Set CLOUDINARY_URL to enable uploads.')
        return redirect(request.referrer or url_for('portfolio'))

    if 'file' not in request.files:
        flash('No file selected')
        return redirect(request.referrer or url_for('portfolio'))

    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(request.referrer or url_for('portfolio'))

    if not (file and allowed_file(file.filename)):
        flash('Invalid file type. Please upload a video file.')
        return redirect(url_for('portfolio'))

    # Read extra fields
    title = request.form.get('title', '').strip() or 'Uploaded Video'
    description = request.form.get('description', '').strip()
    category = (request.form.get('category', 'coding') or 'coding').strip().lower()
    if category not in ALLOWED_CATEGORIES:
        category = 'coding'

    try:
        # Upload to Cloudinary as video
        upload_result = cloudinary.uploader.upload_large(
            file.stream,
            resource_type='video',
            folder='portfolio_uploads',
            use_filename=True,
            unique_filename=True,
        )

        video_url = upload_result.get('secure_url')
        public_id = upload_result.get('public_id')

        if not video_url or not public_id:
            raise RuntimeError('Upload failed: missing URL or public_id')

        # Save metadata to database
        with SessionLocal() as db:
            video = Video(public_id=public_id, url=video_url, title=title, description=description, category=category)
            db.add(video)
            db.commit()

        flash('Video uploaded successfully!')
    except SQLAlchemyError as e:
        flash('Database error while saving video metadata.')
        if app.debug:
            flash(str(e))
    except Exception as e:
        msg = 'Error uploading video. Please try again.'
        if app.debug:
            msg = f'{msg} Details: {str(e)}'
        flash(msg)

    return redirect(url_for('portfolio'))

@app.route('/videos/<int:video_id>/delete', methods=['POST'])
@login_required
def delete_video(video_id: int):
    try:
        with SessionLocal() as db:
            video = db.query(Video).filter(Video.id == video_id).first()
            if not video:
                flash('Video not found.')
                return redirect(url_for('portfolio'))
            # Try to remove from Cloudinary (best-effort)
            try:
                if os.getenv('CLOUDINARY_URL') and video.public_id:
                    cloudinary.uploader.destroy(video.public_id, resource_type='video', invalidate=True)
            except Exception as cloud_err:
                if app.debug:
                    flash(f'Cloud delete warning: {cloud_err}')
            # Remove from DB
            db.delete(video)
            db.commit()
        flash('Video deleted.')
    except SQLAlchemyError as e:
        flash('Database error while deleting video.')
        if app.debug:
            flash(str(e))
    return redirect(url_for('portfolio'))

# Image gallery endpoints
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}

def allowed_image(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

@app.route('/upload_image', methods=['POST'])
@login_required
def upload_image():
    if not os.getenv('CLOUDINARY_URL'):
        flash('Cloudinary is not configured. Set CLOUDINARY_URL to enable uploads.')
        return redirect(request.referrer or url_for('portfolio'))

    if 'image' not in request.files:
        flash('No image selected')
        return redirect(request.referrer or url_for('portfolio'))

    img = request.files['image']
    if img.filename == '':
        flash('No image selected')
        return redirect(request.referrer or url_for('portfolio'))

    if not (img and allowed_image(img.filename)):
        flash('Invalid file type. Please upload an image file.')
        return redirect(url_for('portfolio'))

    title = request.form.get('title', '').strip() or 'Photo'
    description = request.form.get('description', '').strip()
    category = (request.form.get('category', 'work') or 'work').strip().lower()

    try:
        up = cloudinary.uploader.upload(img.stream, resource_type='image', folder='portfolio_images', use_filename=True, unique_filename=True)
        url = up.get('secure_url')
        public_id = up.get('public_id')
        if not url or not public_id:
            raise RuntimeError('Upload failed: missing URL or public_id')
        with SessionLocal() as db:
            image = Image(public_id=public_id, url=url, title=title, description=description, category=category)
            db.add(image)
            db.commit()
        flash('Image uploaded successfully!')
    except SQLAlchemyError as e:
        flash('Database error while saving image metadata.')
        if app.debug:
            flash(str(e))
    except Exception as e:
        msg = 'Error uploading image. Please try again.'
        if app.debug:
            msg = f'{msg} Details: {str(e)}'
        flash(msg)
    return redirect(url_for('portfolio'))

@app.route('/images/<int:image_id>/delete', methods=['POST'])
@login_required
def delete_image(image_id: int):
    try:
        with SessionLocal() as db:
            image = db.query(Image).filter(Image.id == image_id).first()
            if not image:
                flash('Image not found.')
                return redirect(url_for('portfolio'))
            try:
                if os.getenv('CLOUDINARY_URL') and image.public_id:
                    cloudinary.uploader.destroy(image.public_id, resource_type='image', invalidate=True)
            except Exception as cloud_err:
                if app.debug:
                    flash(f'Cloud delete warning: {cloud_err}')
            db.delete(image)
            db.commit()
        flash('Image deleted.')
    except SQLAlchemyError as e:
        flash('Database error while deleting image.')
        if app.debug:
            flash(str(e))
    return redirect(url_for('portfolio'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['is_admin'] = True
            flash('Logged in successfully.')
            next_url = request.args.get('next') or url_for('portfolio')
            return redirect(next_url)
        flash('Invalid credentials.')
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('is_admin', None)
    flash('Logged out.')
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
