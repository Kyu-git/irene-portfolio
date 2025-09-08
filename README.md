# Kha's Portfolio Website

A modern, responsive portfolio website showcasing both full-stack development and hairdressing skills. Built with Flask and featuring video uploads, interactive galleries, and a professional design.

## Features

- **Dual Profession Showcase**: Highlights both coding and hairdressing expertise
- **Video Portfolio**: Upload and display coding tutorials and hairdressing videos
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **Modern UI/UX**: Clean, professional design with smooth animations
- **Interactive Elements**: Filterable video galleries and contact forms
- **Security Focus**: Built with cybersecurity best practices in mind

## Technologies Used

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **Styling**: Custom CSS with modern gradients and animations
- **Icons**: Font Awesome
- **Fonts**: Google Fonts (Poppins)

## Education Background

- **Degree**: Bachelor of Computer Security and Forensics
- **Institution**: Meru University of Science and Technology
- **Specialization**: Cybersecurity, Digital Forensics, Network Security

## Services Offered

### Technical Services
- Full Stack Web Development (Python, JavaScript, React)
- Cybersecurity Consultation
- Digital Forensics
- Security Assessments
- API Development

### Creative Services
- Professional Hairdressing
- Hair Styling and Coloring
- Bridal Hair Services
- Hair Care Consultation

## Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd my-profile-website
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment variables**
   Create a `.env` file at the project root with:
   ```
   SECRET_KEY=change-me
   DATABASE_URL=postgresql://user:password@host:5432/dbname
   CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:5000`

## Project Structure

```
my-profile-website/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── static/
│   ├── css/
│   │   └── style.css     # Main stylesheet
│   ├── js/
│   │   └── script.js     # JavaScript functionality
│   └── uploads/          # Video upload directory
└── templates/
    ├── base.html         # Base template
    ├── index.html        # Homepage
    ├── about.html        # About page
    ├── portfolio.html    # Portfolio page
    └── contact.html      # Contact page
```

## Features Overview

### Homepage
- Hero section with dual profession introduction
- Services overview cards
- About preview section
- Portfolio highlights
- Call-to-action sections

### About Page
- Personal story and background
- Education details (Meru University)
- Skills showcase with categories
- Professional experience timeline
- Personal philosophy

### Portfolio Page
- Filterable video galleries (Coding & Hairdressing)
- Video upload functionality
- Project highlights
- Technical skills demonstration
- Interactive filtering system

### Contact Page
- Professional contact form
- Service selection dropdown
- Contact information display
- FAQ section
- Social media links

## Video Upload

The website supports video uploads for both coding and hairdressing content:

- **Supported formats**: MP4, AVI, MOV, WMV, FLV, WebM
- **Maximum file size**: 100MB
- **Upload location**: `static/uploads/`
- **Security**: File validation and secure filename handling

## Customization

### Personal Information
Update the following in your templates:
- Name and title in `templates/index.html`
- Contact information in `templates/contact.html`
- Social media links in `templates/base.html`
- About content in `templates/about.html`

### Styling
- Modify `static/css/style.css` for color schemes and layouts
- Update gradients and animations as needed
- Responsive breakpoints can be adjusted in the CSS

### Content
- Add your own videos to the `static/uploads/` directory
- Update portfolio content in `templates/portfolio.html`
- Modify service descriptions in `templates/contact.html`

## Security Features

- File upload validation
- Secure filename handling
- CSRF protection (Flask-WTF recommended for production)
- Input sanitization
- Secure session management

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Deployment

For production deployment:

1. **Set a secure secret key** in `app.py`
2. **Use a production WSGI server** (e.g., Gunicorn)
3. **Set up a reverse proxy** (e.g., Nginx)
4. **Configure SSL/HTTPS**
5. **Set up proper file storage** (e.g., AWS S3 for video files)
6. **Implement proper logging and monitoring**

## Contributing

This is a personal portfolio website. If you'd like to use it as a template:

1. Fork the repository
2. Customize the content for your needs
3. Update personal information and styling
4. Deploy to your preferred platform

## License

This project is open source and available under the MIT License.

## Contact

For questions about this portfolio template or collaboration opportunities:

- **Email**: your.email@example.com
- **Phone**: +254 XXX XXX XXX
- **Location**: Kenya

---

Built with ❤️ by Kha - Full Stack Developer & Professional Hairdresser
