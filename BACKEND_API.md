# Backend API Server Template for Video Compliance Framework

This is a Flask-based REST API server that handles video processing requests from the React frontend.

## Installation

### Prerequisites

- Python 3.8+
- FFmpeg (already required by VideoPreprocessor.py)
- Your existing Python packages (opencv-python, numpy)

### Setup

1. **Install additional Python packages**

   ```bash
   pip install flask flask-cors python-dotenv
   ```

2. **For production deployment, install Gunicorn**
   ```bash
   pip install gunicorn
   ```

## Configuration

Create a `.env` file in the backend root:

```env
FLASK_ENV=development
FLASK_DEBUG=True
API_HOST=0.0.0.0
API_PORT=5000
UPLOAD_FOLDER=uploads
OUTPUT_FOLDER=preprocessed_output
MAX_FILE_SIZE=5368709120
```

## Running the Server

### Development

```bash
python app.py
```

The API will be available at `http://localhost:5000`

### Production

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## API Endpoints

### 1. POST /api/process-video

**Process a video file**

**Request:**

- Method: `POST`
- Content-Type: `multipart/form-data`
- Parameters:
  - `video` (file, required) - Video file to process
  - `sampleFps` (number, default: 2.0) - Frames per second to extract
  - `modelSize` (string, default: base) - Whisper model size
  - `wordLevel` (boolean, default: false) - Word-level transcription timestamps

**Example:**

```bash
curl -X POST http://localhost:5000/api/process-video \
  -F "video=@video.mp4" \
  -F "sampleFps=2" \
  -F "modelSize=base" \
  -F "wordLevel=false"
```

**Response (202 Accepted):**

```json
{
  "jobId": "550e8400-e29b-41d4-a716-446655440000",
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Video processing started"
}
```

---

### 2. GET /api/job-status/:jobId

**Check job processing status**

**Request:**

```bash
curl http://localhost:5000/api/job-status/550e8400-e29b-41d4-a716-446655440000
```

**Response (while processing):**

```json
{
  "status": "processing",
  "progress": 45,
  "message": "Extracting frames and audio...",
  "data": null
}
```

**Response (completed):**

```json
{
  "status": "completed",
  "progress": 100,
  "message": "Processing complete!",
  "data": {
    "duration": 120.5,
    "originalFps": 30,
    "sampleFps": 2,
    "frames": [
      {
        "frame_id": 0,
        "timestamp_sec": 0.0,
        "file_path": "/path/to/frame_0.png"
      }
    ],
    "transcription": "[00:00:00 - 00:00:05] Sample text...",
    "audioPath": "/path/to/audio.wav",
    "metadataPath": "/path/to/metadata.json",
    "framesZipPath": "/path/to/frames.zip"
  }
}
```

**Response (error):**

```json
{
  "status": "error",
  "progress": 0,
  "message": "Error: Unsupported video format",
  "data": null,
  "error": "Unsupported video format"
}
```

---

### 3. GET /api/download

**Download processed files**

**Query Parameters:**

- `file` (required) - File path to download (relative to project root)

**Example:**

```bash
curl http://localhost:5000/api/download?file=preprocessed_output/job_id/audio.wav \
  -o audio.wav
```

**Returns:** Binary file stream

---

### 4. GET /api/health

**Health check endpoint**

**Request:**

```bash
curl http://localhost:5000/api/health
```

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2024-03-17T10:30:45.123456"
}
```

---

### 5. GET /

**API information**

**Request:**

```bash
curl http://localhost:5000/
```

**Response:**

```json
{
  "message": "Video Compliance Framework API",
  "version": "1.0.0",
  "endpoints": {
    "POST /api/process-video": "Process a video file",
    "GET /api/job-status/<job_id>": "Check job status",
    "GET /api/download": "Download processed files",
    "GET /api/health": "Health check"
  }
}
```

## Integration with Frontend

The React frontend expects the API to be running and accessible at the URL specified in the `REACT_APP_API_URL` environment variable.

1. **Start the backend server**

   ```bash
   python app.py
   ```

2. **Set frontend environment**

   ```bash
   cd frontend
   echo "REACT_APP_API_URL=http://localhost:5000" > .env.local
   ```

3. **Start the frontend**
   ```bash
   npm start
   ```

## File Structure After Processing

When a video is processed, the following structure is created:

```
preprocessed_output/
├── <job_id>/
│   ├── frames/
│   │   ├── frame_0.png
│   │   ├── frame_1.png
│   │   └── ...
│   ├── audio.wav
│   ├── metadata.json
│   └── frames.zip
```

## Job States

1. **pending** - Job created, waiting to start
2. **processing** - Actively processing
3. **completed** - Successfully processed
4. **error** - Processing failed

## Frontend Integration Flow

1. User uploads video in React frontend
2. Frontend sends POST request to `/api/process-video`
3. Backend returns `jobId` and starts processing in background thread
4. Frontend polls `/api/job-status/{jobId}` every 1 second
5. User sees progress bar and status updates
6. When status = "completed", frontend displays results
7. User can download files via `/api/download` endpoint

## Error Handling

### Common Errors

| Error                         | Cause                   | Solution                                                |
| ----------------------------- | ----------------------- | ------------------------------------------------------- |
| "No video file provided"      | Missing file in request | Check form-data includes video file                     |
| "File type not allowed"       | Unsupported extension   | Use MP4, MOV, MKV, AVI, or WebM                         |
| "File size exceeds 5GB limit" | File too large          | Use smaller video or raise MAX_FILE_SIZE                |
| "Job not found"               | Invalid jobId           | Check job ID returned from process-video                |
| "Internal server error"       | Backend crash           | Check server logs and ensure all dependencies installed |

## Performance Tips

1. **Adjust worker count** for production:

   ```bash
   gunicorn -w 8 -b 0.0.0.0:5000 app:app
   ```

2. **Enable caching** for downloaded files
3. **Use Redis** for job state instead of in-memory dict (for production)
4. **Set max concurrent processes** to avoid overwhelming the server
5. **Monitor system resources** (CPU, memory, disk space)

## Troubleshooting

### Port 5000 Already in Use

```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9

# Or use different port
python app.py --port=5001
```

### CORS Errors

Ensure Flask-CORS is properly configured in `app.py`:

```python
CORS(app)  # Allows all domains
```

### Jobs Not Processing

- Check if backend threads are running
- Verify VideoPreprocessor.py works independently
- Check system resources (CPU, disk space)
- Look at server logs

### Files Not Found on Download

- Verify file path is correct
- Check file permissions
- Ensure output folder exists

## Next Steps

1. Test the API using cURL or Postman
2. Run the frontend and test end-to-end
3. Deploy to production with Gunicorn/Nginx
4. Set up monitoring and logging
5. Configure cloud storage for output files (optional)

## Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Flask-CORS Documentation](https://flask-cors.readthedocs.io/)
- [Gunicorn Documentation](https://gunicorn.org/)
