AI Resume Scorer - FastAPI Application 🚀
Overview
A production-ready AI-powered resume scoring system built with FastAPI that automatically analyzes PDF resumes against job descriptions using Natural Language Processing (NLP). The application provides instant compatibility scores and stores results in a PostgreSQL database.

Tech Stack
Backend: Python, FastAPI

Database: PostgreSQL with SQLAlchemy ORM

NLP Processing: scikit-learn, TF-IDF, Cosine Similarity

PDF Handling: PyPDF2

Frontend: HTML/CSS with Jinja2 templates

Architecture: RESTful API with MVC pattern

Project Structure
text
resume-scorer/
├── main.py          # FastAPI application & routes
├── database.py      # Database configuration
├── models.py        # SQLAlchemy data models
├── requirements.txt # Dependencies
├── templates/       # HTML templates
│   ├── index.html   # Main interface
│   ├── results.html # Results page
│   └── error.html   # Error handling
└── README.md        # Documentation
Core Features
1. PDF Text Extraction
Automatic text extraction from uploaded PDF resumes

Encrypted PDF detection and handling

Validation for image-based/scanned PDFs

Error handling for corrupted files

2. AI-Powered Scoring
TF-IDF Vectorization: Converts text to numerical representations

Cosine Similarity: Measures semantic similarity between resume and job description

Keyword Extraction: Automatically identifies important terms from job descriptions

Multi-algorithm Approach: Combines TF-IDF with keyword matching

3. Database Integration
PostgreSQL for production with SQLite development option

SQLAlchemy ORM for database operations

Automatic table creation and schema management

Score history tracking with timestamps

4. Web Interface
User-friendly file upload interface

Real-time scoring results

Historical score display

Responsive error handling

API Endpoints
Web Interface
Method	Endpoint	Description
GET	/	Main web interface for resume upload
POST	/	Process form submission and display results
REST API Endpoints
Method	Endpoint	Description	Parameters
POST	/score	Score resume against job description	file (PDF), job_desc (string)
GET	/scores	Retrieve last 10 score records	None
POST	/debug-extract	Test PDF text extraction	file (PDF)
Request/Response Examples
Score a Resume
Request:

bash
curl -X POST -F "file=@resume.pdf" -F "job_desc=Python developer with FastAPI experience" http://localhost:8000/score
Response:

json
{
  "status": "success",
  "score": 85.5,
  "text_length": 2450,
  "record_id": 15,
  "resume_preview": "John Doe Python Developer...",
}
Get Score History
Request:

bash
curl http://localhost:8000/scores
Response:

json
{
  "results": [
    {
      "id": 15,
      "score": 85.5,
      "analyzed_at": "2024-01-15T10:30:00"
    }
  ]
}
Database Schema
ResumeScore Table
Column	Type	Description
id	Integer	Primary key, auto-increment
user_id	Integer	Future user association
resume_text	String	Extracted text (first 5000 chars)
job_desc	String	Job description text
score	Float	Compatibility score (0-100)
missing_skills	String	JSON string of missing skills
analyzed_at	DateTime	Analysis timestamp
User Table (Future Enhancement)
Column	Type	Description
id	Integer	Primary key
username	String	Unique username
hashed_password	String	Password hash
