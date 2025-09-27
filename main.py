from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import PyPDF2
import io
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from collections import Counter
import numpy as np

# Database imports
from models import ResumeScore, Base
from database import SessionLocal, engine

# Create tables in the database
Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper function to extract text from PDF
def extract_text_from_pdf(file_contents: bytes) -> str:
    try:
        pdf = PyPDF2.PdfReader(io.BytesIO(file_contents))
        text = ""
        
        # Check if PDF is encrypted
        if pdf.is_encrypted:
            try:
                pdf.decrypt('')  # Try empty password
            except:
                raise HTTPException(status_code=400, detail="PDF is password protected")
        
        for page in pdf.pages:
            page_text = page.extract_text() or ""  # Handle None returns
            text += page_text + " "
        
        # If no text extracted, PDF might be scanned/image-based
        if not text.strip():
            raise HTTPException(status_code=400, detail="PDF appears to be image-based (no extractable text)")
        
        return text.strip()
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PDF processing failed: {str(e)}")

# Keyword extraction function
def extract_keywords(text, max_keywords=15):
    """Extract important keywords from text using TF-IDF"""
    if not text or not text.strip():
        return []
        
    # Clean text
    text = re.sub(r'[^\w\s]', ' ', text.lower())
    words = text.split()
    
    if len(words) < 3:
        return words  # Return all words if text is very short
    
    # Use TF-IDF to find important words
    vectorizer = TfidfVectorizer(stop_words='english', max_features=100)
    try:
        tfidf_matrix = vectorizer.fit_transform([text])
        feature_names = vectorizer.get_feature_names_out()
        tfidf_scores = tfidf_matrix.toarray()[0]
        
        # Get top keywords by TF-IDF score
        keyword_indices = np.argsort(tfidf_scores)[::-1][:max_keywords]
        keywords = [feature_names[i] for i in keyword_indices if tfidf_scores[i] > 0]
        
        return keywords if keywords else words[:max_keywords]
    except:
        # Fallback: return most frequent words
        return [word for word, count in Counter(words).most_common(max_keywords)]

# Keyword matching function
def calculate_keyword_match(resume_text, job_desc):
    """Calculate score based on keyword matching"""
    if not resume_text or not job_desc:
        return 0, [], []
        
    # Extract keywords from job description
    job_keywords = extract_keywords(job_desc)
    
    # Clean resume text
    resume_clean = re.sub(r'[^\w\s]', ' ', resume_text.lower())
    resume_words = set(resume_clean.split())
    
    # Find matching keywords
    matching_keywords = [kw for kw in job_keywords if kw in resume_words]
    
    # Calculate score based on keyword match percentage
    if job_keywords:
        keyword_score = (len(matching_keywords) / len(job_keywords)) * 100
    else:
        keyword_score = 0
    
    return keyword_score, matching_keywords, job_keywords

# Main scoring function (SIMPLIFIED - to fix the error)
def calculate_score(resume_text: str, job_desc: str) -> float:
    try:
        # Basic text cleaning
        resume_clean = ' '.join(resume_text.lower().split())
        job_clean = ' '.join(job_desc.lower().split())
        
        # If texts are empty after cleaning
        if not resume_clean or not job_clean:
            return 0.0
        
        # Simple TF-IDF scoring (remove complex logic for now)
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform([resume_clean, job_clean])
        similarity = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]
        
        score = max(0, min(100, similarity * 100))
        return round(score, 2)
        
    except Exception as e:
        print(f"Scoring error: {e}")
        # Fallback: simple word matching
        resume_words = set(resume_text.lower().split())
        job_words = set(job_desc.lower().split())
        common_words = resume_words.intersection(job_words)
        
        if job_words:
            return round((len(common_words) / len(job_words)) * 100, 2)
        return 0.0

# Debug endpoint to check text extraction
@app.post("/debug-extract")
async def debug_extract(file: UploadFile = File(...)):
    """Debug endpoint to test PDF extraction"""
    try:
        contents = await file.read()
        resume_text = extract_text_from_pdf(contents)
        return {
            "status": "success",
            "extracted_text_length": len(resume_text),
            "extracted_text_preview": resume_text[:500] + "..." if len(resume_text) > 500 else resume_text,
            "is_text_extracted": len(resume_text.strip()) > 0
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

# API Endpoint to score AND save resume
@app.post("/score")
async def score_resume(
    file: UploadFile = File(...), 
    job_desc: str = "",
    db: Session = Depends(get_db)
):
    """Score resume and save to database"""
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Extract text from PDF
        contents = await file.read()
        resume_text = extract_text_from_pdf(contents)
        
        # Calculate score
        score = calculate_score(resume_text, job_desc)
        
        # Save to database
        db_score = ResumeScore(
            resume_text=resume_text[:5000],
            job_desc=job_desc,
            score=score
        )
        db.add(db_score)
        db.commit()
        db.refresh(db_score)
        
        return {
            "status": "success",
            "score": score,
            "text_length": len(resume_text),
            "record_id": db_score.id,
            "resume_preview": resume_text[:200] + "..." 
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process resume: {str(e)}")

# New endpoint to fetch historical scores
@app.get("/scores")
async def get_scores(db: Session = Depends(get_db)):
    scores = db.query(ResumeScore).order_by(ResumeScore.id.desc()).limit(10).all()
    return {"results": [
        {"id": s.id, "score": s.score, "analyzed_at": s.analyzed_at} 
        for s in scores
    ]}

# HTML form endpoint
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Form processing endpoint
@app.post("/", response_class=HTMLResponse)
async def process_resume(
    request: Request,
    file: UploadFile = File(...),
    job_desc: str = Form(...),
    db: Session = Depends(get_db)
):
    """Process form submission from HTML"""
    try:
        contents = await file.read()
        resume_text = extract_text_from_pdf(contents)
        score = calculate_score(resume_text, job_desc)
        
        # Save to database
        db_score = ResumeScore(
            resume_text=resume_text[:5000],
            job_desc=job_desc,
            score=score
        )
        db.add(db_score)
        db.commit()
        
        # Get recent scores for display
        recent_scores = db.query(ResumeScore).order_by(ResumeScore.id.desc()).limit(5).all()
        
        return templates.TemplateResponse("results.html", {
            "request": request,
            "score": score,
            "resume_preview": resume_text[:200] + "...",
            "text_length": len(resume_text),
            "recent_scores": recent_scores
        })
        
    except Exception as e:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": str(e)
        })