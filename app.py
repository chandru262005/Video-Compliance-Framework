"""
Video Compliance Framework - Flask Backend API
This Flask server handles video processing and provides API endpoints for the React frontend.

Installation:
    pip install flask flask-cors python-dotenv

Run:
    python app.py
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import json
import uuid
import threading
from pathlib import Path
from datetime import datetime

# Import your video processing modules
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from VideoPreprocessor import preprocess_video
from AudioToText import transcribe_audio

# Configuration
app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'preprocessed_output'
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'mkv', 'avi', 'webm'}
MAX_FILE_SIZE = 5 * 1024 * 1024 * 1024  # 5GB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# In-memory job tracking
jobs = {}


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def process_video_job(job_id, video_path, sample_fps, model_size, word_level):
    """Background job to process video"""
    try:
        jobs[job_id]['status'] = 'processing'
        jobs[job_id]['message'] = 'Extracting frames and audio...'
        jobs[job_id]['progress'] = 0

        # Process video - extract frames and audio
        output_dir = os.path.join(OUTPUT_FOLDER, job_id)
        os.makedirs(output_dir, exist_ok=True)

        # Call your VideoPreprocessor
        result = preprocess_video(
            video_path=video_path,
            output_base_dir=output_dir,
            sample_fps=sample_fps
        )

        jobs[job_id]['progress'] = 50
        jobs[job_id]['message'] = 'Transcribing audio (this may take a few minutes)...'

        # Transcribe audio with optimizations
        audio_path = result.audio_path
        # Use 'tiny' model for fast transcription, user can select larger models from frontend
        optimized_model = 'tiny' if model_size == 'base' else model_size
        transcription = transcribe_audio(audio_path, model_size=optimized_model, word_level=word_level)

        jobs[job_id]['progress'] = 90
        jobs[job_id]['message'] = 'Generating results...'

        # Prepare response data
        frames_data = []
        for frame_info in result.frames:
            frames_data.append({
                'frame_id': frame_info.frame_id,
                'timestamp_sec': frame_info.timestamp_sec,
                'file_path': frame_info.file_path,
                'preview': frame_info.file_path  # In production, generate base64 preview
            })

        response_data = {
            'duration': result.duration_sec,
            'originalFps': result.original_fps,
            'sampleFps': result.sample_fps,
            'frames': frames_data,
            'transcription': transcription,
            'audioPath': audio_path,
            'metadataPath': result.metadata_path,
            'framesZipPath': os.path.join(output_dir, 'frames.zip'),
            'jobId': job_id
        }

        jobs[job_id]['status'] = 'completed'
        jobs[job_id]['progress'] = 100
        jobs[job_id]['message'] = 'Processing complete!'
        jobs[job_id]['data'] = response_data

        # Cleanup uploaded file
        if os.path.exists(video_path):
            os.remove(video_path)

    except Exception as e:
        jobs[job_id]['status'] = 'error'
        jobs[job_id]['message'] = f'Error: {str(e)}'
        jobs[job_id]['error'] = str(e)
        print(f"Job {job_id} error: {str(e)}")


@app.route('/api/process-video', methods=['POST'])
def process_video_endpoint():
    """
    Endpoint to process video
    Form data:
        - video: video file
        - sampleFps: frames per second to extract
        - modelSize: whisper model size
        - wordLevel: boolean for word-level timestamps
    """
    try:
        # Check if file was uploaded
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400

        file = request.files['video']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400

        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        if file_size > MAX_FILE_SIZE:
            return jsonify({'error': 'File size exceeds 5GB limit'}), 400

        # Get parameters
        sample_fps = float(request.form.get('sampleFps', 2.0))
        model_size = request.form.get('modelSize', 'base')
        word_level = request.form.get('wordLevel', 'false').lower() == 'true'

        # Save uploaded file
        job_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        video_path = os.path.join(UPLOAD_FOLDER, f"{job_id}_{filename}")
        file.save(video_path)

        # Create job entry
        jobs[job_id] = {
            'status': 'pending',
            'progress': 0,
            'message': 'Starting processing...',
            'createdAt': datetime.now().isoformat()
        }

        # Start processing in background thread
        thread = threading.Thread(
            target=process_video_job,
            args=(job_id, video_path, sample_fps, model_size, word_level)
        )
        thread.daemon = True
        thread.start()

        return jsonify({
            'jobId': job_id,
            'id': job_id,
            'message': 'Video processing started'
        }), 202

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/api/job-status/<job_id>', methods=['GET'])
def job_status(job_id):
    """Get job processing status"""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404

    job = jobs[job_id]
    return jsonify({
        'status': job['status'],
        'progress': job.get('progress', 0),
        'message': job.get('message', ''),
        'data': job.get('data'),
        'error': job.get('error')
    }), 200


@app.route('/api/download', methods=['GET'])
def download_file():
    """Download processed files"""
    try:
        file_path = request.args.get('file')
        if not file_path:
            return jsonify({'error': 'No file specified'}), 400

        # Security: prevent directory traversal
        file_path = os.path.normpath(file_path)
        if '..' in file_path:
            return jsonify({'error': 'Invalid file path'}), 400

        full_path = os.path.join(os.getcwd(), file_path)

        if not os.path.exists(full_path):
            return jsonify({'error': 'File not found'}), 404

        return send_file(full_path, as_attachment=True)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/', methods=['GET'])
def index():
    """Root endpoint"""
    return jsonify({
        'message': 'Video Compliance Framework API',
        'version': '1.0.0',
        'endpoints': {
            'POST /api/process-video': 'Process a video file',
            'GET /api/job-status/<job_id>': 'Check job status',
            'GET /api/download': 'Download processed files',
            'GET /api/health': 'Health check'
        }
    }), 200


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Development server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )

    # For production, use:
    # gunicorn -w 4 -b 0.0.0.0:5000 app:app
