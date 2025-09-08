from flask import Flask, render_template, request, redirect, url_for, flash
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from sqlalchemy import create_engine, String, DateTime
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
    category: Mapped[str] = mapped_column(String(50), default='coding')
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
    return render_template("portfolio.html", videos=videos)

@app.route('/contact')
def contact():
    return render_template("contact.html")

@app.route('/upload', methods=['POST'])
def upload_file():
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

    try:
        # Upload to Cloudinary as video
        upload_result = cloudinary.uploader.upload_large(
            file,
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
            video = Video(public_id=public_id, url=video_url)
            db.add(video)
            db.commit()

        flash('Video uploaded successfully!')
    except SQLAlchemyError:
        flash('Database error while saving video metadata.')
    except Exception as e:
        flash('Error uploading video. Please try again.')

    return redirect(url_for('portfolio'))

if __name__ == "__main__":
    app.run(debug=True)
