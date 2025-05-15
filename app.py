import os
import logging
import tempfile
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from werkzeug.utils import secure_filename
from yt_translator import YouTubeTranslator

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Ensure temp directory exists for file storage
TEMP_DIR = os.path.join(tempfile.gettempdir(), 'yt_translator')
os.makedirs(TEMP_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate():
    youtube_url = request.form.get('youtube_url')
    
    if not youtube_url:
        flash('Please provide a YouTube URL', 'danger')
        return redirect(url_for('index'))
    
    try:
        translator = YouTubeTranslator()
        
        # Start translation process and get job ID
        job_id = translator.start_translation_job(youtube_url)
        
        # Store job ID in session
        session['job_id'] = job_id
        
        # Redirect to result page
        return redirect(url_for('result'))
    
    except Exception as e:
        logger.error(f"Error during translation: {str(e)}")
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/result')
def result():
    job_id = session.get('job_id')
    
    if not job_id:
        flash('No translation job found', 'warning')
        return redirect(url_for('index'))
    
    try:
        translator = YouTubeTranslator()
        status = translator.get_job_status(job_id)
        
        if status['status'] == 'completed':
            download_url = url_for('download_file', filename=status['filename'])
            return render_template('result.html', status=status, download_url=download_url)
        else:
            return render_template('result.html', status=status)
    
    except Exception as e:
        logger.error(f"Error checking job status: {str(e)}")
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/status/<job_id>')
def job_status(job_id):
    try:
        translator = YouTubeTranslator()
        status = translator.get_job_status(job_id)
        return status
    except Exception as e:
        logger.error(f"Error getting job status: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(TEMP_DIR, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
