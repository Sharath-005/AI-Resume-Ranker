from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import traceback
import logging

# Import the necessary functions from the ranker module
from ranker import extract_text_from_file, calculate_scores, preload_model

# Set up basic logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
# Enable Cross-Origin Resource Sharing
CORS(app)

# Configure the upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload size

@app.route('/')
def index():
    """A simple route to confirm the server is running."""
    return "The AI Resume Ranker server is running."

@app.route('/rank', methods=['POST'])
def rank_resume():
    """The main endpoint to handle resume ranking."""
    try:
        if 'resume' not in request.files:
            return jsonify({"error": "No resume file part in the request"}), 400

        resume_file = request.files['resume']
        job_description = request.form.get('job_description', '')

        if resume_file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        if not job_description.strip():
            return jsonify({"error": "Job description cannot be empty"}), 400

        filename = secure_filename(resume_file.filename)
        resume_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save the file temporarily
        resume_file.save(resume_path)

        # Extract text from the saved file
        resume_text = extract_text_from_file(resume_path)

        if not resume_text:
            os.remove(resume_path) # Clean up the file
            return jsonify({"error": "Could not extract text from the file. It might be empty, corrupted, or an unsupported format."}), 400

        # Calculate the scores using the ranking logic
        scores = calculate_scores(job_description, resume_text)

        # Clean up the uploaded file after processing
        os.remove(resume_path)

        return jsonify({
            "filename": filename,
            "semantic_score": scores["semantic_score"],
            "keyword_overlap_score": scores["keyword_overlap_score"],
            "matched_keywords": scores["matched_keywords"]
        })

    except Exception as e:
        # Log the full error for debugging
        app.logger.error(f"An error occurred during ranking: {e}")
        traceback.print_exc()
        # Return a generic error to the user
        return jsonify({"error": "An internal server error occurred. Please check the server logs."}), 500

if __name__ == '__main__':
    # --- CRITICAL FIX ---
    # Preload the AI model before starting the server.
    # This moves the long loading time from the first request to the startup phase,
    # preventing browser timeouts.
    app.logger.info("Starting Flask server...")
    app.logger.info("Loading AI model... (This may take a moment on the first run)")
    preload_model()
    app.logger.info("AI model loaded successfully. Server is ready.")
    
    # Run the Flask app with HTTPS enabled to match the browser's security context.
    # The 'cryptography' library must be installed for 'ssl_context' to work.
    # Run: pip install cryptography
    app.run(host='0.0.0.0', port=5001, debug=True, ssl_context='adhoc')

