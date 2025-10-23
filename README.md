# AI-Resume-Ranker
AI-powered web app that analyzes and ranks resumes against job descriptions using Natural Language Processing (NLP) and semantic similarity.

# 🧠 AI Resume Ranker

An **AI-powered web application** that evaluates and ranks resumes based on their **relevance to a given job description**, using **Natural Language Processing (NLP)** and **semantic similarity scoring**.

## 🚀 Features
- 🔍 **Semantic Analysis:** Uses SentenceTransformer (`all-MiniLM-L6-v2`) to calculate text similarity between resumes and job descriptions.  
- 🧩 **Keyword Matching:** Identifies overlapping key skills and terms between the job and the resume.  
- 📄 **Multi-format Resume Parsing:** Supports `.pdf`, `.docx`, and `.txt` file uploads.  
- ⚡ **Real-time Results:** Provides semantic score, keyword overlap score, and matched keywords instantly.  
- 🌐 **User-friendly Frontend:** Clean and responsive HTML/CSS/JavaScript interface for easy interaction.  
- 🔒 **Secure Backend:** Flask-based API with CORS support and controlled file handling.

## 🛠️ Tech Stack
**Frontend:** HTML5, CSS3, JavaScript  
**Backend:** Python (Flask), REST API  
**AI/NLP:** Sentence Transformers (`all-MiniLM-L6-v2`)  
**Libraries:** PyPDF2, python-docx, flask-cors, werkzeug  

## ⚙️ How It Works
1. The user uploads a resume and pastes a job description.  
2. The Flask backend extracts text from the resume.  
3. The SentenceTransformer model computes semantic similarity.  
4. The app returns a **semantic match score**, **keyword overlap score**, and the list of **matched keywords**.  
5. Results are displayed neatly on the frontend with visual feedback.  

## 📦 Installation & Setup
```bash
# Clone the repository
git clone https://github.com/Sharath-005/AI-Resume-Ranker.git
cd AI-Resume-Ranker

# Install dependencies
pip install -r requirements.txt

# Run the Flask server
python app.py

# Open in browser
http://localhost:5001
