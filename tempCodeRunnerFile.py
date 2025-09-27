from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import PyPDF2
import io
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from models import ResumeScore, Base
from database import SessionLocal, engine
from database import Base, engine

# Create tables in the database
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Serve static files and templates
# app.mount("/static", StaticFiles(directory="static"), name="static")
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
            page_text = page.extract_text()
            if page_text.strip():  # Only add non-empty text
                text += page_text + " "
        
        # If no text extracted, PDF might be scanned/image-based
        if not text.strip():
            raise HTTPException(status_code=400, detail="PDF appears to be image-based (no extractable text)")
        
        return text.strip()
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PDF processing failed: {str(e)}")
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import re

def extract_keywords(text, max_keywords=15):
    """Extract important keywords from text using TF-IDF"""
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
        from collections import Counter
        return [word for word, count in Counter(words).most_common(max_keywords)]

# Helper function to calculate similarity score
def calculate_score(resume_text: str, job_desc: str) -> float:
    try:
        # Clean texts
        resume_clean = resume_text.lower()
        job_clean = job_desc.lower()
        
        # Method 1: Keyword-based scoring
        keyword_score, matched_keywords, all_keywords = calculate_keyword_match(resume_clean, job_clean)
        
        # Method 2: TF-IDF similarity (original method)
        vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        tfidf_matrix = vectorizer.fit_transform([resume_clean, job_clean])
        tfidf_score = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0] * 100
        
        # Method 3: Simple word overlap (fallback)
        resume_words = set(resume_clean.split())
        job_words = set(job_clean.split())
        overlap_score = (len(resume_words.intersection(job_words)) / len(job_words)) * 100 if job_words else 0
        
        # Combine scores (weighted average)
        final_score = (keyword_score * 0.5) + (tfidf_score * 0.3) + (overlap_score * 0.2)
        
        # Ensure score is reasonable
        final_score = max(0, min(100, final_score))
        
        # Debug info (you can remove this later)
        print(f"Keywords extracted: {all_keywords}")
        print(f"Matched keywords: {matched_keywords}")
        print(f"Keyword score: {keyword_score:.2f}%")
        print(f"TF-IDF score: {tfidf_score:.2f}%")
        print(f"Overlap score: {overlap_score:.2f}%")
        
        return round(final_score, 2)
        
    except Exception as e:
        print(f"Scoring error: {e}")
        return 0.0
# Debug endpoint to check text extraction

def calculate_keyword_match(resume_text, job_desc):
    """Calculate score based on keyword matching"""
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
@app.post("/debug-extract")
async def debug_extract(file: UploadFile = File(...)):
    contents = await file.read()
    resume_text = extract_text_from_pdf(contents)
    return {"extracted_text": resume_text}

# API Endpoint to score AND save resume
@app.post("/score")
async def score_resume(
    file: UploadFile = File(...), 
    job_desc: str = "",
    db: Session = Depends(get_db)
):
    contents = await file.read()
    resume_text = extract_text_from_pdf(contents)
    
    # Calculate score with keyword analysis
    keyword_score, matched_keywords, all_keywords = calculate_keyword_match(
        resume_text.lower(), 
        job_desc.lower()
    )
    
    tfidf_score = calculate_score(resume_text, job_desc)  # This now uses the enhanced algorithm
    
    # Save to database
    db_score = ResumeScore(
        resume_text=resume_text[:5000],
        job_desc=job_desc,
        score=tfidf_score
    )
    db.add(db_score)
    db.commit()
    db.refresh(db_score)
    
    return {
        "status": "success",
        "score": tfidf_score,
        "keyword_analysis": {
            "total_keywords": len(all_keywords),
            "matched_keywords": len(matched_keywords),
            "extracted_keywords": all_keywords[:10],  # First 10 keywords
            "matched_keywords_list": matched_keywords
        },
        "text_length": len(resume_text),
        "record_id": db_score.id
    }
# New endpoint to fetch historical scores
@app.get("/scores")
async def get_scores(db: Session = Depends(get_db)):
    scores = db.query(ResumeScore).order_by(ResumeScore.id.desc()).limit(10).all()
    return {"results": [
        {"id": s.id, "score": s.score, "analyzed_at": s.analyzed_at} 
        for s in scores
    ]}

# Serve the HTML page
@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})