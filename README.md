# 🧾 AI-Powered ATS Resume Parser

> “A smart resume screening engine that understands structure, content, and relevance — built for MAANG-level hiring standards.”

The **ATS Resume Parser** is a full-stack, AI-enhanced system designed to automatically **analyze, score, and filter resumes** based on job descriptions — simulating how top-tier companies’ **Applicant Tracking Systems (ATS)** process resumes.  

This project showcases **Python NLP, FastAPI, and PDF parsing** combined with a **modern scoring algorithm** for developer-level automation.

---

## 🚀 Key Features

| Feature | Description |
|----------|-------------|
| 📄 **PDF/Docx Resume Parsing** | Extracts text, skills, education, and experience from uploaded resumes. |
| 🧠 **AI Keyword Matching** | Compares resume keywords with job descriptions using NLP. |
| 📊 **ATS Compatibility Score** | Calculates how well a resume aligns with a job posting (0–100%). |
| 🧠 **OpenAI Integration (optional)** | Generates resume improvement suggestions using AI. |
| 📦 **FastAPI Backend** | High-performance, scalable backend for parsing and scoring. |
| 🌐 **React/HTML Frontend (optional)** | Simple UI for uploading resumes and displaying results. |
| 💾 **Database Integration (optional)** | Store parsed data and scores using PostgreSQL or SQLite. |
| 🧠 **Job Description Analyzer** | Extracts key role requirements automatically. |

---

## 🧩 Project Architecture



This modular setup is inspired by **enterprise-grade architectures** — with a clean separation of layers.

---

## ⚙️ Tech Stack

| Layer | Technology |
|--------|-------------|
| **Backend Framework** | FastAPI |
| **Text Extraction** | PyMuPDF / pdfminer.six / python-docx |
| **NLP Processing** | spaCy / NLTK / Scikit-learn |
| **Database** | PostgreSQL / SQLite |
| **Frontend (optional)** | HTML + JavaScript or React |
| **AI API (optional)** | OpenAI GPT or HuggingFace Models |
| **Language** | Python 3.13 |

---

## 🧠 End-to-End Workflow

1. **📤 Resume Upload**
   - User uploads a resume (`.pdf` or `.docx`) through the web interface or API.

2. **🧾 Resume Parsing**
   - The backend extracts raw text using `PyMuPDF` or `docx` libraries.
   - Extracts structured information (skills, experience, education).

3. **🧠 Job Description Analysis**
   - A job description is provided or uploaded.
   - The system uses **TF-IDF/NLP** to identify keywords and requirements.

4. **🔍 Keyword Matching**
   - Resume and job description are compared via semantic similarity or keyword overlap.

5. **📊 ATS Score Calculation**
   - Final score (0–100%) is generated based on:
     - Skill match %
     - Keyword density
     - Role relevance
     - Experience alignment

6. **📈 Output**
   - JSON or UI view showing:
     - ATS Score
     - Missing Skills
     - Strengths
     - AI-based resume tips

---

## 🧠 Example Output

```json
{
  "name": "Dhruv Redhu",
  "score": 87,
  "matched_skills": ["Python", "FastAPI", "SQLAlchemy", "Machine Learning"],
  "missing_skills": ["AWS", "CI/CD"],
  "summary": "Your resume is highly aligned with the SDE role. Adding deployment and DevOps exposure will improve your score."
}


🛠️ Installation & Setup

1️⃣ Clone the Repository
git clone https://github.com/YOUR_USERNAME/ATS-Resume-Parser.git
cd ATS-Resume-Parser

2️⃣ Create a Virtual Environment
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Run the App
uvicorn main:app --reload

Server starts → http://127.0.0.1:8000

🧠 Example API Usage
POST /upload-resume
Content-Type: multipart/form-data
File: resume.pdf

🧠 Submit Job Description
POST /job-description
Body: {
  "text": "We are hiring for a Software Engineer with experience in Python, AWS, and FastAPI..."
}

📊 Get ATS Score
GET /score

📦 Requirements
fastapi
uvicorn
python-multipart
pymupdf
python-docx
spacy
nltk
scikit-learn
sqlalchemy
openai      # (optional)

🌟 Features in Development

🔍 Resume Ranking System (compare multiple resumes)
🧠 AI Resume Suggestions (using OpenAI)
🧾 Export Scored Resume as PDF
📊 Interactive Dashboard for Recruiters
☁️ Cloud Resume Storage

🧩 Scalability & Code Design

✅ Modular microservice design for easy extension
✅ Clear separation between parsing, matching, and scoring
✅ Follows SOLID and clean architecture principles
✅ Ready for integration with AI-powered job-matching APIs

🌍 Deployment Options
| Service                             | Purpose                        |
| ----------------------------------- | ------------------------------ |
| **Render / Railway / Heroku**       | Host FastAPI backend           |
| **Vercel / Netlify / GitHub Pages** | Host web interface             |
| **Supabase / Neon**                 | Cloud PostgreSQL Database      |
| **Docker**                          | Containerize and deploy easily |

✨ Author

👨‍💻 Dhruv Redhu
Software Engineer | AI Automation & Backend Systems
📍 India

🧠 Summary

The ATS Resume Parser project reimagines how resumes are screened and scored — automating the process that HR teams and big tech companies rely on.
With an AI-backed matching algorithm and FastAPI backbone, this project is ready for real-world deployment and scaling.

“Your resume deserves to be understood — not just scanned.”

⭐ Star this repo if you find it helpful and want more open-source AI systems!












