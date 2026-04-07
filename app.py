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

# Import compliance modules
try:
    from ocr import easyocr_ocr, tesseract_ocr
except ImportError:
    print("Warning: OCR module not available")
    easyocr_ocr = None
    tesseract_ocr = None

try:
    from logo_detect import YOLO
except ImportError:
    print("Warning: Logo detection module not available")
    YOLO = None

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


def extract_text_from_frames(frames_info, output_dir):
    """Extract text from frames using OCR"""
    ocr_results = {
        'detected_text': [],
        'summary': '',
        'text_count': 0
    }
    
    try:
        if not easyocr_ocr:
            return ocr_results
            
        text_buffer = []
        for frame_info in frames_info[:5]:  # Process first 5 frames for speed
            try:
                frame_path = frame_info.file_path if hasattr(frame_info, 'file_path') else None
                if frame_path and os.path.exists(frame_path):
                    text = easyocr_ocr(frame_path)
                    if text.strip():
                        text_buffer.append({
                            'frame_id': frame_info.frame_id if hasattr(frame_info, 'frame_id') else 0,
                            'text': text[:100],  # Store first 100 chars
                            'timestamp': frame_info.timestamp_sec if hasattr(frame_info, 'timestamp_sec') else 0
                        })
            except Exception as e:
                print(f"OCR error on frame: {e}")
                continue
        
        ocr_results['detected_text'] = text_buffer
        ocr_results['text_count'] = len(text_buffer)
        ocr_results['summary'] = f"Detected text in {len(text_buffer)} frames"
        
    except Exception as e:
        print(f"Frame OCR processing error: {e}")
    
    return ocr_results


def detect_logos(frames_info, output_dir):
    """Detect logos in frames using YOLO"""
    logo_results = {
        'detections': [],
        'summary': '',
        'detection_count': 0
    }
    
    try:
        if not YOLO or not os.path.exists('best.pt'):
            return logo_results
        
        try:
            from ultralytics import YOLO as YOLOModel
            model = YOLOModel('best.pt')
        except Exception as e:
            print(f"YOLO load error: {e}")
            return logo_results
        
        detections = []
        for frame_info in frames_info[::max(1, len(frames_info)//10)]:  # Sample 10 frames
            try:
                frame_path = frame_info.file_path if hasattr(frame_info, 'file_path') else None
                if frame_path and os.path.exists(frame_path):
                    results = model.predict(frame_path, conf=0.5, verbose=False)
                    for result in results:
                        if hasattr(result, 'boxes'):
                            for box in result.boxes:
                                confidence = float(box.conf[0]) if hasattr(box.conf, '__getitem__') else float(box.conf)
                                detections.append({
                                    'frame_id': frame_info.frame_id if hasattr(frame_info, 'frame_id') else 0,
                                    'timestamp': frame_info.timestamp_sec if hasattr(frame_info, 'timestamp_sec') else 0,
                                    'confidence': round(confidence, 2),
                                    'class_id': int(box.cls[0]) if hasattr(box.cls, '__getitem__') else int(box.cls)
                                })
            except Exception as e:
                print(f"Logo detection error on frame: {e}")
                continue
        
        logo_results['detections'] = detections
        logo_results['detection_count'] = len(detections)
        logo_results['summary'] = f"Detected {len(detections)} logos across {len([d for d in detections])} frames"
        
    except Exception as e:
        print(f"Logo detection error: {e}")
    
    return logo_results


def check_compliance_rules(transcription_text):
    """Check transcription against compliance rules"""
    compliance_results = {
        'issues': [],
        'warnings': [],
        'passed': True,
        'score': 100
    }
    
    try:
        text_lower = transcription_text.lower()
        
        # Define comprehensive compliance rules
        # Prohibited/High-risk terms
        prohibited_words = [
            'explicit', 'banned', 'violate', 'xxx', 'adult', 'nsfw',
            'hate', 'racist', 'sexist', 'violence', 'kill', 'harm',
            'fraud', 'scam', 'illegal', 'copyright', 'counterfeit',
            'viagra', 'casino', 'lottery', 'bet now', 'gambling',
            'weight loss', 'miracle', 'cure', 'guaranteed 100%',
            'free money', 'easy cash', 'work from home', 'get rich',
            'clickbait', 'loser', 'stupid', 'dumb',
        ]
        
        # Strong ad/promotional call-to-action phrases (aggressive penalties)
        cta_phrases = [
            'buy now', 'shop now', 'order now', 'call now',
            'click here', 'tap here', 'get yours', 'get it now',
            'limited time', 'act fast', 'don\'t miss', 'don\'t wait',
            'exclusive', 'only today', 'today only', 'expires',
            'rush', 'hurry', 'while supplies last',
        ]
        
        # Suspicious product/supplement keywords (not common words)
        product_keywords = [
            'supplement', 'vitamin', 'powder', 'shake', 'pill',
            'weight loss', 'energy boost', 'atomic buzz',
            'detox', 'cleanse', 'extract',
        ]
        
        # Warning terms
        warning_words = [
            'sale', 'discount', 'free', 'offer', 'promo', 'save',
            'limited', 'supply', 'price', 'cost', 'affordable',
            'caution', 'warning', 'attention', 'notice', 'alert',
            'subscription', 'trial', 'premium', 'upgrade',
            'shop', 'buy', 'purchase', 'available now'
        ]
        
        # Check for prohibited content
        for word in prohibited_words:
            count = text_lower.count(word)
            if count > 0:
                compliance_results['issues'].append(f"Prohibited term detected ({count}x): '{word}'")
                compliance_results['passed'] = False
                compliance_results['score'] -= (20 * count)
        
        # Check for strong CTA phrases (aggressive penalty)
        cta_found = False
        for phrase in cta_phrases:
            count = text_lower.count(phrase)
            if count > 0:
                compliance_results['issues'].append(f"Strong call-to-action detected: '{phrase}'")
                compliance_results['score'] -= 30  # Heavy penalty for CTAs
                cta_found = True
                compliance_results['passed'] = False
        
        # Check for product keywords (indicates promotional content)
        product_mentions = 0
        for keyword in product_keywords:
            if keyword in text_lower:
                product_mentions += 1
                compliance_results['warnings'].append(f"Product/brand mention: '{keyword}'")
                compliance_results['score'] -= 30  # Increased penalty for suspicious products
        
        if product_mentions > 1:
            compliance_results['issues'].append(f"Multiple product mentions detected ({product_mentions})")
            compliance_results['passed'] = False
            compliance_results['score'] -= 40
        
        # Check for warnings
        for word in warning_words:
            count = text_lower.count(word)
            if count > 0:
                compliance_results['warnings'].append(f"Warning term found ({count}x): '{word}'")
                compliance_results['score'] -= (5 * count)
        
        # Detect excessive exclamation marks (manipulative tone)
        exclamation_count = text_lower.count('!')
        if exclamation_count > 2:
            compliance_results['issues'].append(f"Excessive exclamation marks ({exclamation_count}) - manipulative tone detected")
            compliance_results['score'] -= (10 * (exclamation_count - 2))
            compliance_results['passed'] = False
        
        # Check if it's an ad/promotional content
        ad_keywords = ['buy', 'sale', 'discount', 'free', 'offer', 'shop', 'order', 'price', 'limited', 'get', 'now']
        ad_count = sum(text_lower.count(keyword) for keyword in ad_keywords)
        
        if ad_count > 5:
            compliance_results['issues'].append(f"High ad/promo density detected ({ad_count} promotional keywords)")
            compliance_results['score'] -= 25
            compliance_results['passed'] = False
        elif ad_count > 3:
            compliance_results['warnings'].append(f"Moderate ad/promo density ({ad_count} promotional keywords)")
            compliance_results['score'] -= 15
        
        # Check length
        word_count = len(transcription_text.split())
        if word_count < 10:
            compliance_results['warnings'].append("Transcription is very short")
            compliance_results['score'] -= 3
        
        # Ensure score is between 0-100
        compliance_results['score'] = max(0, min(100, compliance_results['score']))
        
        # Determine pass/fail based on score and issues
        if len(compliance_results['issues']) > 0:
            compliance_results['passed'] = False
        
        if compliance_results['score'] < 60:
            compliance_results['passed'] = False
        
    except Exception as e:
        print(f"Compliance check error: {e}")
    
    return compliance_results


def generate_compliance_report(job_id, processing_data):
    """Generate overall compliance report"""
    report = {
        'job_id': job_id,
        'timestamp': datetime.now().isoformat(),
        'video_analysis': {},
        'text_analysis': {},
        'logo_analysis': {},
        'compliance': {},
        'overall_status': 'PASSED',
        'overall_score': 100
    }
    
    try:
        # Add video metadata
        report['video_analysis'] = {
            'duration': processing_data.get('duration', 0),
            'fps': processing_data.get('sampleFps', 0),
            'frame_count': len(processing_data.get('frames', []))
        }
        
        # Add OCR data
        ocr_data = processing_data.get('ocr_results', {})
        report['text_analysis'] = {
            'method': 'Optical Character Recognition (OCR)',
            'detected_frames': ocr_data.get('text_count', 0),
            'summary': ocr_data.get('summary', 'No text detected'),
            'samples': ocr_data.get('detected_text', [])[:3]
        }
        
        # Add logo detection data
        logo_data = processing_data.get('logo_results', {})
        report['logo_analysis'] = {
            'method': 'YOLO-based Logo Detection',
            'logos_detected': logo_data.get('detection_count', 0),
            'summary': logo_data.get('summary', 'No logos detected'),
            'detections': logo_data.get('detections', [])[:5]
        }
        
        # Add compliance check data
        compliance_data = processing_data.get('compliance_results', {})
        report['compliance'] = {
            'transcript_validation': 'Passed' if compliance_data.get('passed', True) else 'Failed',
            'score': compliance_data.get('score', 100),
            'issues': compliance_data.get('issues', []),
            'warnings': compliance_data.get('warnings', [])
        }
        
        # Calculate overall status
        overall_score = compliance_data.get('score', 100)
        logo_suspicion = logo_data.get('detection_count', 0) > 10
        text_issues = len(compliance_data.get('issues', [])) > 0
        
        if overall_score < 60 or text_issues:
            report['overall_status'] = 'FAILED'
        elif overall_score < 80 or logo_suspicion:
            report['overall_status'] = 'REVIEW_REQUIRED'
        else:
            report['overall_status'] = 'PASSED'
        
        report['overall_score'] = overall_score
        
    except Exception as e:
        print(f"Report generation error: {e}")
        report['overall_status'] = 'ERROR'
    
    return report


def process_video_job(job_id, video_path, sample_fps, model_size, word_level):
    """Background job to process video with full compliance checks"""
    try:
        jobs[job_id]['status'] = 'processing'
        jobs[job_id]['message'] = 'Step 1/7: Extracting frames and audio...'
        jobs[job_id]['progress'] = 0

        # STEP 1: Extract frames and audio
        output_dir = os.path.join(OUTPUT_FOLDER, job_id)
        os.makedirs(output_dir, exist_ok=True)

        print(f"Starting video preprocessing for job {job_id}")
        result = preprocess_video(
            video_path=video_path,
            output_base_dir=output_dir,
            sample_fps=sample_fps
        )
        
        # STEP 2: Transcribe audio
        jobs[job_id]['progress'] = 20
        jobs[job_id]['message'] = 'Step 2/7: Transcribing audio...'
        print(f"Video preprocessing complete, starting transcription for job {job_id}")

        audio_path = result.audio_path
        try:
            transcription_result = transcribe_audio(audio_path, model_size=model_size, word_level=word_level)
            if isinstance(transcription_result, dict):
                transcription_text = transcription_result.get('text', transcription_result.get('transcription', ''))
            else:
                transcription_text = str(transcription_result)
        except Exception as e:
            print(f"Transcription error: {e}, traceback: {traceback.format_exc()}")
            transcription_text = f"[Transcription failed: {str(e)}]"

        # STEP 3: Extract text from frames using OCR
        jobs[job_id]['progress'] = 35
        jobs[job_id]['message'] = 'Step 3/7: Extracting text from frames (OCR)...'
        print(f"Starting OCR analysis for job {job_id}")
        
        frames_list = result.frames if hasattr(result, 'frames') and result.frames else []
        ocr_results = extract_text_from_frames(frames_list, output_dir)

        # STEP 4: Detect logos in frames
        jobs[job_id]['progress'] = 50
        jobs[job_id]['message'] = 'Step 4/7: Detecting logos...'
        print(f"Starting logo detection for job {job_id}")
        
        logo_results = detect_logos(frames_list, output_dir)

        # STEP 5: Check compliance rules
        jobs[job_id]['progress'] = 65
        jobs[job_id]['message'] = 'Step 5/7: Checking compliance rules...'
        print(f"Starting compliance check for job {job_id}")
        
        compliance_results = check_compliance_rules(transcription_text)

        # STEP 6: Prepare frames data for display
        jobs[job_id]['progress'] = 75
        jobs[job_id]['message'] = 'Step 6/7: Preparing frames for display...'

        frames_data = []
        if frames_list:
            for idx, frame_info in enumerate(frames_list):
                frame_file = os.path.basename(frame_info.file_path) if hasattr(frame_info, 'file_path') else f"frame_{idx:05d}.png"
                relative_path = f"{OUTPUT_FOLDER}/{job_id}/frames/{frame_file}"
                preview = generate_frame_thumbnail(frame_info.file_path) if hasattr(frame_info, 'file_path') else relative_path
                
                frames_data.append({
                    'frame_id': frame_info.frame_id if hasattr(frame_info, 'frame_id') else idx,
                    'timestamp_sec': frame_info.timestamp_sec if hasattr(frame_info, 'timestamp_sec') else (idx / sample_fps),
                    'file_path': relative_path,
                    'preview': preview or relative_path
                })

        frames_zip = create_frames_zip(output_dir, job_id)
        audio_relative = f"{OUTPUT_FOLDER}/{job_id}/audio/audio.wav"
        metadata_relative = f"{OUTPUT_FOLDER}/{job_id}/metadata.json"

        # STEP 7: Generate overall compliance report
        jobs[job_id]['progress'] = 90
        jobs[job_id]['message'] = 'Step 7/7: Generating compliance report...'
        print(f"Generating report for job {job_id}")

        # Prepare data for report
        response_data = {
            'duration': result.duration_sec if hasattr(result, 'duration_sec') else 0,
            'originalFps': result.original_fps if hasattr(result, 'original_fps') else 0,
            'sampleFps': result.sample_fps if hasattr(result, 'sample_fps') else sample_fps,
            'frames': frames_data,
            'transcription': transcription_text,
            'audioPath': audio_relative,
            'metadataPath': metadata_relative,
            'framesZipPath': frames_zip,
            'jobId': job_id,
            'ocr_results': ocr_results,
            'logo_results': logo_results,
            'compliance_results': compliance_results
        }

        # Generate comprehensive report
        compliance_report = generate_compliance_report(job_id, response_data)
        response_data['compliance_report'] = compliance_report

        jobs[job_id]['status'] = 'completed'
        jobs[job_id]['progress'] = 100
        jobs[job_id]['message'] = 'Compliance analysis complete!'
        jobs[job_id]['data'] = response_data
        
        print(f"Job {job_id} completed successfully")
        print(f"Overall Status: {compliance_report['overall_status']} | Score: {compliance_report['overall_score']}/100")

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


@app.route('/api/download-report/<job_id>', methods=['GET'])
def download_report(job_id):
    """Download compliance report in various formats"""
    try:
        format_type = request.args.get('format', 'json').lower()  # json, csv, html
        
        if job_id not in jobs:
            return jsonify({'error': 'Job not found'}), 404
        
        job = jobs[job_id]
        if job['status'] != 'completed':
            return jsonify({'error': 'Job not yet completed'}), 400
        
        report = job.get('data', {}).get('compliance_report', {})
        if not report:
            return jsonify({'error': 'No report available'}), 404
        
        if format_type == 'json':
            # Return as JSON file download
            buffer = BytesIO(json.dumps(report, indent=2).encode('utf-8'))
            buffer.seek(0)
            return send_file(
                buffer,
                mimetype='application/json',
                as_attachment=True,
                download_name=f'compliance_report_{job_id}.json'
            )
        
        elif format_type == 'csv':
            # Convert report to CSV format
            import csv
            buffer = BytesIO()
            text_buffer = BytesIO()
            
            # Create CSV with report summary
            lines = []
            lines.append(f"Compliance Report - {job_id}")
            lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append("")
            lines.append("OVERALL RESULTS")
            lines.append(f"Status,{report.get('overall_status', 'N/A')}")
            lines.append(f"Score,{report.get('overall_score', 0)}/100")
            lines.append("")
            
            lines.append("VIDEO ANALYSIS")
            video = report.get('video_analysis', {})
            lines.append(f"Duration (seconds),{video.get('duration', 0)}")
            lines.append(f"Frames Per Second,{video.get('fps', 0)}")
            lines.append(f"Total Frames,{video.get('frame_count', 0)}")
            lines.append("")
            
            lines.append("TEXT ANALYSIS (OCR)")
            text = report.get('text_analysis', {})
            lines.append(f"Method,{text.get('method', 'N/A')}")
            lines.append(f"Frames Analyzed,{text.get('detected_frames', 0)}")
            lines.append("")
            
            lines.append("LOGO ANALYSIS")
            logo = report.get('logo_analysis', {})
            lines.append(f"Method,{logo.get('method', 'N/A')}")
            lines.append(f"Logos Detected,{logo.get('logos_detected', 0)}")
            lines.append("")
            
            lines.append("COMPLIANCE RESULTS")
            comp = report.get('compliance', {})
            lines.append(f"Validation Result,{comp.get('transcript_validation', 'N/A')}")
            lines.append(f"Compliance Score,{comp.get('score', 0)}")
            lines.append(f"Issues Found,{len(comp.get('issues', []))}")
            lines.append(f"Warnings Found,{len(comp.get('warnings', []))}")
            lines.append("")
            
            if comp.get('issues'):
                lines.append("ISSUES DETECTED")
                for issue in comp.get('issues', []):
                    lines.append(f'"{issue}"')
                lines.append("")
            
            if comp.get('warnings'):
                lines.append("WARNINGS")
                for warning in comp.get('warnings', []):
                    lines.append(f'"{warning}"')
            
            csv_content = '\n'.join(lines)
            buffer = BytesIO(csv_content.encode('utf-8'))
            buffer.seek(0)
            return send_file(
                buffer,
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'compliance_report_{job_id}.csv'
            )
        
        elif format_type == 'html':
            # Generate HTML report
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Compliance Report - {job_id}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #667eea; padding-bottom: 10px; }}
        h2 {{ color: #667eea; margin-top: 30px; }}
        .status-badge {{ display: inline-block; padding: 10px 20px; border-radius: 5px; font-weight: bold; color: white; }}
        .status-passed {{ background: #4CAF50; }}
        .status-failed {{ background: #f44336; }}
        .status-review {{ background: #ff9800; }}
        .score-circle {{ width: 120px; height: 120px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: bold; color: white; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin: 20px 0; }}
        .section {{ margin: 20px 0; padding: 15px; background: #f9f9f9; border-left: 4px solid #667eea; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #667eea; color: white; }}
        tr:hover {{ background: #f5f5f5; }}
        .issue {{ color: #f44336; padding: 5px; margin: 5px 0; }}
        .warning {{ color: #ff9800; padding: 5px; margin: 5px 0; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; text-align: center; color: #999; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Video Compliance Report</h1>
        <p><strong>Job ID:</strong> {job_id}</p>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <h2>Overall Status</h2>
        <div class="status-badge status-{report.get('overall_status', 'review').lower()}">
            {report.get('overall_status', 'UNKNOWN')}
        </div>
        <div class="score-circle">{report.get('overall_score', 0)}</div>
        <p><strong>Compliance Score:</strong> {report.get('overall_score', 0)}/100</p>
        
        <h2>Video Analysis</h2>
        <div class="section">
            <table>
                <tr><th>Metric</th><th>Value</th></tr>
                <tr><td>Duration (seconds)</td><td>{report.get('video_analysis', {}).get('duration', 0)}</td></tr>
                <tr><td>Frames Per Second</td><td>{report.get('video_analysis', {}).get('fps', 0)}</td></tr>
                <tr><td>Total Frames</td><td>{report.get('video_analysis', {}).get('frame_count', 0)}</td></tr>
            </table>
        </div>
        
        <h2>Text Analysis (OCR)</h2>
        <div class="section">
            <p><strong>Method:</strong> {report.get('text_analysis', {}).get('method', 'N/A')}</p>
            <p><strong>Frames Analyzed:</strong> {report.get('text_analysis', {}).get('detected_frames', 0)}</p>
            <p><strong>Summary:</strong> {report.get('text_analysis', {}).get('summary', 'N/A')}</p>
        </div>
        
        <h2>Logo Analysis</h2>
        <div class="section">
            <p><strong>Method:</strong> {report.get('logo_analysis', {}).get('method', 'N/A')}</p>
            <p><strong>Logos Detected:</strong> {report.get('logo_analysis', {}).get('logos_detected', 0)}</p>
            <p><strong>Summary:</strong> {report.get('logo_analysis', {}).get('summary', 'N/A')}</p>
        </div>
        
        <h2>Compliance Results</h2>
        <div class="section">
            <p><strong>Transcript Validation:</strong> {report.get('compliance', {}).get('transcript_validation', 'N/A')}</p>
            <p><strong>Compliance Score:</strong> {report.get('compliance', {}).get('score', 0)}</p>
"""
            
            # Add issues
            issues = report.get('compliance', {}).get('issues', [])
            if issues:
                html_content += "<h3>Issues Found</h3>"
                for issue in issues:
                    html_content += f'<div class="issue">⚠️ {issue}</div>'
            
            # Add warnings
            warnings = report.get('compliance', {}).get('warnings', [])
            if warnings:
                html_content += "<h3>Warnings</h3>"
                for warning in warnings:
                    html_content += f'<div class="warning">⚡ {warning}</div>'
            
            html_content += """
        </div>
        
        <div class="footer">
            <p>Video Compliance Framework Report</p>
            <p>This report was automatically generated by the compliance analysis system.</p>
        </div>
    </div>
</body>
</html>
"""
            
            buffer = BytesIO(html_content.encode('utf-8'))
            buffer.seek(0)
            return send_file(
                buffer,
                mimetype='text/html',
                as_attachment=True,
                download_name=f'compliance_report_{job_id}.html'
            )
        
        else:
            return jsonify({'error': 'Unsupported format. Use: json, csv, or html'}), 400
    
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
        port=8000,
        debug=True
    )

    # For production, use:
    # gunicorn -w 4 -b 0.0.0.0:5000 app:app
