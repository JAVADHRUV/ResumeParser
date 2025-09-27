from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ✅ Replace 'your_new_password' with the password you just set
DATABASE_URL = "postgresql://postgres:Admin@localhost:5432/resume_scorer"

# Create engine
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

print("✅ Database configuration updated with new password!")