from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import requests
import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Backend API URL
BACKEND_URL = 'http://localhost:8003'

# Configure upload settings
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    # Initialize chat history in session if it doesn't exist
    if 'chat_history' not in session:
        session['chat_history'] = []
    
    # Get list of patent documents from backend
    try:
        response = requests.get(f"{BACKEND_URL}/patent-documents")
        if response.status_code == 200:
            patent_documents = response.json().get('documents', [])
        else:
            patent_documents = []
    except Exception:
        patent_documents = []
    
    return render_template('index.html', 
                           chat_history=session['chat_history'],
                           patent_documents=patent_documents)

@app.route('/ask', methods=['POST'])
def ask():
    # Get the question from the form
    question = request.form.get('question')
    
    if not question:
        return jsonify({'error': 'No question provided'}), 400
    
    try:
        # Call the backend API
        response = requests.post(
            f"{BACKEND_URL}/ask",
            json={"question": question}
        )
        
        if response.status_code == 200:
            answer_data = response.json()
            answer = answer_data.get('answer', 'No answer provided')
            
            # Add to chat history
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            chat_entry = {
                'id': str(uuid.uuid4()),
                'question': question,
                'answer': answer,
                'timestamp': timestamp
            }
            
            # Update session
            chat_history = session.get('chat_history', [])
            chat_history.append(chat_entry)
            session['chat_history'] = chat_history
            
            return jsonify({
                'success': True,
                'answer': answer,
                'chat_entry': chat_entry
            })
        else:
            return jsonify({
                'success': False,
                'error': f"Backend error: {response.status_code}",
                'message': response.text
            }), response.status_code
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f"Error connecting to backend: {str(e)}"
        }), 500

@app.route('/clear-history', methods=['POST'])
def clear_history():
    session['chat_history'] = []
    return jsonify({'success': True})

@app.route('/upload-patent', methods=['POST'])
def upload_patent():
    # Check if a file was uploaded
    if 'patent_file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['patent_file']
    
    # Check if file was selected
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    # Check if file is allowed
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Send file to backend for ingestion
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (filename, f)}
                response = requests.post(f"{BACKEND_URL}/upload-patent", files=files)
            
            if response.status_code == 200:
                flash('Patent document uploaded successfully')
            else:
                flash(f'Error uploading patent: {response.text}')
        except Exception as e:
            flash(f'Error: {str(e)}')
        
        return redirect(url_for('index'))
    
    flash('Invalid file type. Allowed types: pdf, docx, txt')
    return redirect(url_for('index'))

@app.route('/analyze-patent', methods=['POST'])
def analyze_patent():
    patent_number = request.form.get('patent_number', '')
    analysis_type = request.form.get('analysis_type', 'general')
    
    try:
        # Call the backend API
        response = requests.post(
            f"{BACKEND_URL}/analyze-patent",
            json={
                "patent_number": patent_number,
                "analysis_type": analysis_type
            }
        )
        
        if response.status_code == 200:
            analysis_data = response.json()
            analysis = analysis_data.get('analysis', 'No analysis provided')
            
            # Add to chat history
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            question = f"Analyze patent {patent_number} for {analysis_type}"
            chat_entry = {
                'id': str(uuid.uuid4()),
                'question': question,
                'answer': analysis,
                'timestamp': timestamp
            }
            
            # Update session
            chat_history = session.get('chat_history', [])
            chat_history.append(chat_entry)
            session['chat_history'] = chat_history
            
            return jsonify({
                'success': True,
                'analysis': analysis,
                'chat_entry': chat_entry
            })
        else:
            return jsonify({
                'success': False,
                'error': f"Backend error: {response.status_code}",
                'message': response.text
            }), response.status_code
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f"Error connecting to backend: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)