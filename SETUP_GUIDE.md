# Complete Video Compliance Framework - Full Stack Setup

This guide walks through setting up and running the entire Video Compliance Framework (frontend + backend).

## Project Overview

```
Video-Compliance-Framework/
├── backend (Python)
│   ├── VideoPreprocessor.py    - Extracts frames & audio from video
│   ├── AudioToText.py          - Transcribes audio using Whisper
│   ├── app.py                  - Flask API server (NEW)
│   └── BACKEND_API.md          - Backend documentation
├── frontend (React)
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── README.md
```

## Part 1: Backend Setup

### Step 1.1: Install Python Dependencies

```bash
# Navigate to project root
cd Video-Compliance-Framework

# Install all required Python packages
pip install opencv-python numpy flask flask-cors python-dotenv faster-whisper
```

**Package Versions:**

- opencv-python >= 4.0
- numpy >= 1.19
- flask >= 2.0
- flask-cors >= 3.0
- faster-whisper >= 0.8 (for audio transcription)

### Step 1.2: Verify FFmpeg Installation

Check if FFmpeg is installed and accessible:

```bash
ffmpeg -version
```

If not installed:

- **Windows**: Download from https://ffmpeg.org/download.html and add to PATH
- **Mac**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg`

### Step 1.3: Start Backend Server

```bash
python app.py
```

**Expected output:**

```
* Running on http://0.0.0.0:5000
* WARNING: This is a development server...
Press CTRL+C to quit
```

## Part 2: Frontend Setup

### Step 2.1: Install Node.js

Download and install from https://nodejs.org/ (LTS recommended)

Verify installation:

```bash
node --version
npm --version
```

### Step 2.2: Install Frontend Dependencies

```bash
# Navigate to frontend directory
cd frontend

# Install all npm packages
npm install
```

This installs:

- react & react-dom (UI library)
- axios (HTTP client)
- lucide-react (icons)
- react-router-dom (routing)

### Step 2.3: Configure Frontend

Create `.env.local` file:

```bash
cd frontend
echo "REACT_APP_API_URL=http://localhost:5000" > .env.local
```

### Step 2.4: Start Frontend Development Server

```bash
npm start
```

**Expected output:**

```
Compiled successfully!

You can now view video-compliance-frontend in the browser.
Local:            http://localhost:3000
```

## Part 3: End-to-End Testing

### Step 3.1: Access the Application

1. Open browser to `http://localhost:3000`
2. You should see the Video Compliance Framework homepage

### Step 3.2: Test Video Processing

1. **Upload a test video**
   - Drag & drop or click to select
   - Use a small test video (< 100MB recommended)
   - Supported formats: MP4, MOV, MKV, AVI, WebM

2. **Configure settings**
   - Sample FPS: 2 (default, adjust as needed)
   - Model Size: "base" (recommended for testing)
   - Word-level: unchecked (faster)

3. **Process**
   - Click "🚀 Process Video"
   - Watch progress bar and status updates
   - Processing time depends on video length and model size

4. **View Results**
   - **Metadata**: Video duration, FPS, frame count
   - **Transcription**: Full text with timestamps
   - **Frames**: Gallery of extracted frames
   - **Downloads**: Export transcription, audio, frames, metadata

### Step 3.3: Download Files

From the Results page:

- **📄 Transcription** - Text file with timestamp
- **🔊 Audio** - WAV file (mono, 16kHz)
- **📦 Frames** - ZIP file with all extracted frames
- **📋 Metadata** - JSON with video information

## Configuration Guide

### Backend Configuration (app.py)

Edit these constants in `app.py`:

```python
UPLOAD_FOLDER = 'uploads'              # Temp folder for uploaded videos
OUTPUT_FOLDER = 'preprocessed_output'  # Output folder for results
MAX_FILE_SIZE = 5 * 1024 * 1024 * 1024 # 5GB limit
ALLOWED_EXTENSIONS = {'.mp4', '.mov', '.mkv', '.avi', '.webm'}
```

### Frontend Configuration (.env.local)

```env
# API Server URL (adjust if backend runs on different host/port)
REACT_APP_API_URL=http://localhost:5000

# Optional for production
REACT_APP_DEBUG=false
```

### VideoPreprocessor Configuration

Edit constants in `VideoPreprocessor.py`:

```python
DEFAULT_SAMPLE_FPS = 2.0        # Frames per second to extract
AUDIO_SAMPLE_RATE = 16000       # Audio sample rate (Hz)
AUDIO_CHANNELS = 1              # Mono audio
SUPPORTED_EXTENSIONS = {        # Supported video formats
    ".mp4", ".mov", ".mkv", ".avi", ".webm"
}
```

### Whisper Model Sizes

In `AudioToText.py`, model_size options:

- **tiny** - Fastest, least accurate (139M)
- **base** - Good balance (244M) - **RECOMMENDED**
- **small** - More accurate (395M)
- **medium** - High accuracy (1.5G)
- **large-v3** - Highest accuracy, slowest (3.1G)

**Model sizes**: First run downloads the model (~size shown above)

## Troubleshooting

### Backend Issues

**Error: "Port 5000 already in use"**

```bash
# Kill the process
lsof -ti:5000 | xargs kill -9

# Or use different port
python app.py --port=5001
```

**Error: "ModuleNotFoundError: No module named 'flask'"**

```bash
pip install flask flask-cors
```

**Error: "FFmpeg not found"**

- Verify FFmpeg installation: `ffmpeg -version`
- Add FFmpeg to PATH environment variable

**Error: "CUDA out of memory"**

- Computer doesn't have enough GPU memory
- Use smaller model size (tiny, base instead of large)
- Or use CPU: set environment variable `CUDA_VISIBLE_DEVICES="""`

### Frontend Issues

**Error: "Cannot find module 'react'"**

```bash
cd frontend
npm install
```

**Error: "API connection failed"**

- Check backend is running: `http://localhost:5000`
- Verify `REACT_APP_API_URL` in `.env.local`
- Check browser console for CORS errors

**Error: "Blank page or 404"**

- Run `npm install` again
- Clear browser cache (Ctrl+Shift+Delete)
- Check Node.js version: `node --version` (should be 14+)

### Processing Issues

**Error: "Unsupported video format"**

- Use one of: MP4, MOV, MKV, AVI, WebM
- Verify file extension is correct

**Error: "Processing timeout"**

- Video is too long or model size is too large
- Try with smaller video or smaller model

## File Structure After Setup

```
Video-Compliance-Framework/
├── app.py                      # Flask backend (NEW)
├── VideoPreprocessor.py
├── AudioToText.py
├── README.md
├── BACKEND_API.md             # API documentation (NEW)
├── frontend/                   # React app (NEW)
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/
│   │   │   ├── VideoUploader.js
│   │   │   ├── VideoUploader.css
│   │   │   ├── ProcessingStatus.js
│   │   │   ├── ProcessingStatus.css
│   │   │   ├── ResultsDisplay.js
│   │   │   └── ResultsDisplay.css
│   │   ├── App.js
│   │   ├── App.css
│   │   ├── index.js
│   │   └── index.css
│   ├── package.json
│   ├── .env.local              # Created during setup
│   ├── .env.example
│   ├── README.md
│   └── .gitignore
├── uploads/                    # Created at runtime (temp files)
└── preprocessed_output/        # Created at runtime (results)
    └── <job_id>/
        ├── frames/
        ├── audio.wav
        └── metadata.json
```

## Production Deployment

### Backend (Production)

```bash
# Install production server
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Or use Nginx + Gunicorn for better performance
```

### Frontend (Production)

```bash
cd frontend

# Build optimized production bundle
npm run build

# Serves optimized static files from build/ folder
# Deploy build/ folder to web server (Nginx, Apache, etc.)
```

### Docker (Optional)

Create `Dockerfile` for entire stack:

```dockerfile
FROM python:3.10

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y ffmpeg nodejs npm

# Copy backend
COPY . .
RUN pip install -r requirements.txt

# Copy and build frontend
WORKDIR /app/frontend
RUN npm install && npm run build

# Set backend env
ENV FLASK_ENV=production

WORKDIR /app
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## Performance Optimization

### Backend

- Use GPU for Whisper (faster transcription)
- Adjust sample FPS based on needs (lower = faster)
- Use smaller Whisper models for speed
- Enable result caching for repeated videos

### Frontend

- Enable gzip compression
- Use CDN for static files
- Optimize images and lazy load frames
- Implement request debouncing

## Monitoring & Logging

### Backend Logs

Add to `app.py`:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### Frontend Debugging

Check browser DevTools:

1. Press F12 to open DevTools
2. Network tab: See API requests/responses
3. Console tab: See errors and logs
4. Application tab: Check stored environment variables

## Next Steps

1. ✅ Backend running on port 5000
2. ✅ Frontend running on port 3000
3. ✅ Tested with sample video
4. 🔄 Deploy to production
5. 🔄 Set up monitoring & backups
6. 🔄 Optimize for your use case

## Support & Documentation

- **Frontend Docs**: See `frontend/README.md`
- **Backend Docs**: See `BACKEND_API.md`
- **Original Project**: See main `README.md`

## Tips for Success

1. **Start small** - Test with short videos first
2. **Monitor resources** - Watch CPU/memory usage
3. **Backup data** - Regular backups of preprocessed_output
4. **Update models** - Whisper models update over time
5. **Scale gradually** - Add load balancing if needed

---

**Ready to process videos!** 🎬

If you encounter issues, check the troubleshooting section or review the log files.
