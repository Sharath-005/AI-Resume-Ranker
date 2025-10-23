import re
from collections import Counter
from sentence_transformers import SentenceTransformer, util
import PyPDF2
import docx
import logging

# Set up basic logging for the ranker module
logging.basicConfig(level=logging.INFO)

# A simple set of common English stopwords
STOPWORDS = {
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", 
    "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", 
    "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", 
    "theirs", "themselves", "what", "which", "who", "whom", "this", "that", 
    "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", 
    "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", 
    "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", 
    "at", "by", "for", "with", "about", "against", "between", "into", "through", 
    "during", "before", "after", "above", "below", "to", "from", "up", "down", 
    "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there"
}

# Regex to find words (including those with special characters like C++)
_WORD_RE = re.compile(r"\b[a-zA-Z0-9'#+.=-]+\b")

# --- Model Loading (Singleton Pattern) ---
# This ensures the model is loaded only once into memory.
_model = None
def _load_model():
    """Loads the SentenceTransformer model into a global variable."""
    global _model
    if _model is None:
        logging.info("[ranker] Loading SentenceTransformer model 'all-MiniLM-L6-v2'...")
        # This model is downloaded from the internet on its first run
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        logging.info("[ranker] SentenceTransformer model loaded successfully.")
    return _model

def preload_model():
    """An explicit function to trigger model loading at app startup."""
    _load_model()

# --- Text Extraction ---
def extract_text_from_pdf(path):
    try:
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as e:
        logging.error(f"[ranker] PDF extraction error for {path}: {e}")
        return ""

def extract_text_from_docx(path):
    try:
        doc = docx.Document(path)
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception as e:
        logging.error(f"[ranker] DOCX extraction error for {path}: {e}")
        return ""

def extract_text_from_txt(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logging.error(f"[ranker] TXT extraction error for {path}: {e}")
        return ""

def extract_text_from_file(path):
    """A wrapper function to handle different file types."""
    if path.lower().endswith(".pdf"):
        return extract_text_from_pdf(path)
    elif path.lower().endswith(".docx"):
        return extract_text_from_docx(path)
    elif path.lower().endswith(".txt"):
        return extract_text_from_txt(path)
    else:
        logging.warning(f"[ranker] Unsupported file type: {path}")
        return ""

# --- Scoring Logic ---
def _get_tokens(text):
    """Cleans and tokenizes text, removing stopwords."""
    if not text:
        return []
    tokens = _WORD_RE.findall(text.lower())
    return [t for t in tokens if t not in STOPWORDS and len(t) > 1]

def keyword_overlap_score(jd_text, resume_text, top_n_keywords=30):
    """Calculates a score based on shared keywords."""
    jd_tokens = _get_tokens(jd_text)
    resume_tokens = _get_tokens(resume_text)
    
    if not jd_tokens or not resume_tokens:
        return {"matched_keywords": [], "score": 0.0}

    # Find the most common keywords in the job description
    jd_keywords = {word for word, count in Counter(jd_tokens).most_common(top_n_keywords)}
    
    # Find which of those keywords appear in the resume
    matched = sorted(list(jd_keywords.intersection(set(resume_tokens))))
    
    score = len(matched) / len(jd_keywords) if jd_keywords else 0.0
    return {"matched_keywords": matched, "score": score}

def semantic_similarity_score(jd_text, resume_text):
    """Calculates cosine similarity between two texts."""
    if not jd_text or not resume_text:
        return 0.0
    model = _load_model()
    # Encode texts to vectors
    jd_emb = model.encode(jd_text, convert_to_tensor=True, show_progress_bar=False)
    res_emb = model.encode(resume_text, convert_to_tensor=True, show_progress_bar=False)
    
    # Calculate cosine similarity
    sim = util.cos_sim(jd_emb, res_emb).item()
    
    # Normalize score from -1..1 to 0..1 for easier interpretation
    return (sim + 1.0) / 2.0

# --- Main API Function ---
def calculate_scores(job_description, resume_text):
    """Calculates and returns all scores."""
    semantic_score = semantic_similarity_score(job_description, resume_text)
    kw_results = keyword_overlap_score(job_description, resume_text)
    
    return {
        "semantic_score": semantic_score,
        "keyword_overlap_score": kw_results["score"],
        "matched_keywords": kw_results["matched_keywords"],
    }

