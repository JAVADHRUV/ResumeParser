# models.py
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class ResumeScore(Base):
    __tablename__ = "resume_scores"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)  # Link to users table
    resume_text = Column(String)
    job_desc = Column(String)
    score = Column(Float)
    missing_skills = Column(String)  # Store as JSON string
    analyzed_at = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    hashed_password = Column(String)