"""
Video Compliance Framework - Flask Backend API
This Flask server handles video processing and provides API endpoints for the React frontend.

Installation:
    pip install flask flask-cors python-dotenv

Run:
    python app.py
"""

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import json
import uuid
import threading
import shutil
import traceback
from pathlib import Path
from datetime import datetime
import base64
from io import BytesIO

# Import your video processing modules
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from VideoPreprocessor import preprocess_video
from AudioToText import transcribe_audio

# Configuration
app = Flask(__name__)
CORS(app, origins="*", allow_headers=["Content-Type"])

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


def generate_frame_thumbnail(frame_path, max_width=200):
    """Generate base64 thumbnail for a frame"""
    try:
        import cv2
        img = cv2.imread(frame_path)
        if img is None:
            return None
        height, width = img.shape[:2]
        scale = max_width / width
        new_width = int(width * scale)
        new_height = int(height * scale)
        resized = cv2.resize(img, (new_width, new_height))
        _, buffer = cv2.imencode('.jpg', resized, [cv2.IMWRITE_JPEG_QUALITY, 85])
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        return f"data:image/jpeg;base64,{img_base64}"
    except Exception as e:
        print(f"Error generating thumbnail: {e}")
        return None


def create_frames_zip(output_dir, job_id):
    """Create a zip file of all frames"""
    try:
        frames_dir = os.path.join(output_dir, 'frames')
        zip_path = os.path.join(output_dir, 'frames')
        
        if os.path.exists(frames_dir):
            shutil.make_archive(zip_path, 'zip', frames_dir)
            return f"{OUTPUT_FOLDER}/{job_id}/frames.zip"
    except Exception as e:
        print(f"Error creating frames zip: {e}")
    return None


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
        print(f"Starting video preprocessing for job {job_id}")
        result = preprocess_video(
            video_path=video_path,
            output_base_dir=output_dir,
            sample_fps=sample_fps
        )
        
        jobs[job_id]['progress'] = 50
        jobs[job_id]['message'] = 'Transcribing audio (this may take a few minutes)...'
        print(f"Video preprocessing complete, starting transcription for job {job_id}")

        # Transcribe audio
        audio_path = result.audio_path
        try:
            transcription_result = transcribe_audio(audio_path, model_size=model_size, word_level=word_level)
            # Handle both string and object responses
            if isinstance(transcription_result, dict):
                transcription_text = transcription_result.get('text', transcription_result.get('transcription', ''))
            else:
                transcription_text = str(transcription_result)
        except Exception as e:
            print(f"Transcription error: {e}, traceback: {traceback.format_exc()}")
            transcription_text = f"[Transcription failed: {str(e)}]"

        jobs[job_id]['progress'] = 85
        jobs[job_id]['message'] = 'Processing frames for display...'

        # Prepare response data
        frames_data = []
        if hasattr(result, 'frames') and result.frames:
            for idx, frame_info in enumerate(result.frames):
                # Create relative file path for API access
                frame_file = os.path.basename(frame_info.file_path) if hasattr(frame_info, 'file_path') else f"frame_{idx:05d}.png"
                relative_path = f"{OUTPUT_FOLDER}/{job_id}/frames/{frame_file}"
                
                # Try to generate thumbnail, fall back to path if fails
                preview = generate_frame_thumbnail(frame_info.file_path) if hasattr(frame_info, 'file_path') else relative_path
                
                frames_data.append({
                    'frame_id': frame_info.frame_id if hasattr(frame_info, 'frame_id') else idx,
                    'timestamp_sec': frame_info.timestamp_sec if hasattr(frame_info, 'timestamp_sec') else (idx / sample_fps),
                    'file_path': relative_path,
                    'preview': preview or relative_path
                })

        jobs[job_id]['progress'] = 90
        jobs[job_id]['message'] = 'Finalizing results...'

        # Create zip of frames
        frames_zip = create_frames_zip(output_dir, job_id)

        # Prepare audio path (relative)
        audio_relative = f"{OUTPUT_FOLDER}/{job_id}/audio/audio.wav"

        # Prepare metadata path (relative)
        metadata_relative = f"{OUTPUT_FOLDER}/{job_id}/metadata.json"

        response_data = {
            'duration': result.duration_sec if hasattr(result, 'duration_sec') else 0,
            'originalFps': result.original_fps if hasattr(result, 'original_fps') else 0,
            'sampleFps': result.sample_fps if hasattr(result, 'sample_fps') else sample_fps,
            'frames': frames_data,
            'transcription': transcription_text,
            'audioPath': audio_relative,
            'metadataPath': metadata_relative,
            'framesZipPath': frames_zip,
            'jobId': job_id
        }

        jobs[job_id]['status'] = 'completed'
        jobs[job_id]['progress'] = 100
        jobs[job_id]['message'] = 'Processing complete!'
        jobs[job_id]['data'] = response_data
        
        print(f"Job {job_id} completed successfully")

        # Cleanup uploaded file
        if os.path.exists(video_path):
            try:
                os.remove(video_path)
            except Exception as e:
                print(f"Error removing uploaded file: {e}")

    except Exception as e:
        print(f"Job {job_id} error: {str(e)}, traceback: {traceback.format_exc()}")
        jobs[job_id]['status'] = 'error'
        jobs[job_id]['message'] = f'Processing failed: {str(e)}'
        jobs[job_id]['error'] = str(e)


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
            return jsonify({'error': 'No video file provided', 'code': 'NO_FILE'}), 400

        file = request.files['video']
        if file.filename == '':
            return jsonify({'error': 'No file selected', 'code': 'EMPTY_FILE'}), 400

        if not allowed_file(file.filename):
            return jsonify({
                'error': f'File type not allowed. Supported: {", ".join(ALLOWED_EXTENSIONS)}',
                'code': 'INVALID_FORMAT'
            }), 400

        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        if file_size > MAX_FILE_SIZE:
            return jsonify({
                'error': 'File size exceeds 5GB limit',
                'code': 'FILE_TOO_LARGE',
                'size': file_size,
                'max': MAX_FILE_SIZE
            }), 400

        # Get parameters with validation
        try:
            sample_fps = float(request.form.get('sampleFps', 2.0))
            if sample_fps < 0.5 or sample_fps > 30:
                sample_fps = 2.0
        except:
            sample_fps = 2.0

        model_size = request.form.get('modelSize', 'base')
        word_level = request.form.get('wordLevel', 'false').lower() == 'true'

        # Save uploaded file
        job_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        video_path = os.path.join(UPLOAD_FOLDER, f"{job_id}_{filename}")
        file.save(video_path)

        print(f"File saved to {video_path}, job_id: {job_id}")

        # Create job entry
        jobs[job_id] = {
            'status': 'pending',
            'progress': 0,
            'message': 'Queued for processing...',
            'createdAt': datetime.now().isoformat(),
            'filename': filename,
            'sampleFps': sample_fps,
            'modelSize': model_size
        }

        # Start processing in background thread
        thread = threading.Thread(
            target=process_video_job,
            args=(job_id, video_path, sample_fps, model_size, word_level),
            daemon=True
        )
        thread.start()

        return jsonify({
            'jobId': job_id,
            'id': job_id,
            'message': 'Video processing started',
            'estimatedTime': 'Will depend on video length and model size'
        }), 202

    except Exception as e:
        print(f"Error in process_video_endpoint: {e}, traceback: {traceback.format_exc()}")
        return jsonify({
            'error': str(e),
            'code': 'PROCESSING_ERROR'
        }), 500


@app.route('/api/job-status/<job_id>', methods=['GET'])
def job_status(job_id):
    """Get job processing status"""
    if job_id not in jobs:
        return jsonify({
            'error': 'Job not found',
            'code': 'JOB_NOT_FOUND'
        }), 404

    job = jobs[job_id]
    response = {
        'status': job['status'],
        'progress': job.get('progress', 0),
        'message': job.get('message', ''),
        'createdAt': job.get('createdAt'),
    }
    
    if job['status'] == 'completed' and 'data' in job:
        response['data'] = job['data']
    
    if job['status'] == 'error' and 'error' in job:
        response['error'] = job['error']
    
    return jsonify(response), 200


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

        # Check if it's a file or directory
        if os.path.isfile(full_path):
            return send_file(full_path, as_attachment=True)
        elif os.path.isdir(full_path):
            # For directories, create a zip on the fly
            import zipfile
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for root, dirs, files in os.walk(full_path):
                    for file in files:
                        file_path_full = os.path.join(root, file)
                        arcname = os.path.relpath(file_path_full, full_path)
                        zip_file.write(file_path_full, arcname)
            zip_buffer.seek(0)
            return send_file(zip_buffer, mimetype='application/zip', 
                           as_attachment=True, download_name='files.zip')
        else:
            return jsonify({'error': 'Invalid file path'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route(f'/{OUTPUT_FOLDER}/<path:filepath>', methods=['GET'])
def serve_output_file(filepath):
    """Serve processed output files (frames, audio)"""
    try:
        full_path = os.path.join(OUTPUT_FOLDER, filepath)
        
        # Security: prevent directory traversal
        if '..' in full_path:
            return jsonify({'error': 'Invalid file path'}), 400
        
        if not os.path.exists(full_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Serve the file
        directory = os.path.dirname(full_path)
        filename = os.path.basename(full_path)
        return send_from_directory(directory, filename)
    
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
