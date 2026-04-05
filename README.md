# Video Compliance Framework

A comprehensive full-stack web application for video processing and analysis. This framework extracts frames, audio, and transcriptions from video files with a modern React frontend and Flask backend API.

---

## 📋 Overview

The **Video Compliance Framework** is a complete system consisting of:

- **Frontend**: React-based UI (port 3000)
- **Backend**: Flask REST API (port 5000)
- **Processing Modules**: Video preprocessing, audio extraction, and transcription
- **Job Management**: Asynchronous processing with real-time status tracking

### Core Features

✅ **Video Processing**

- Frame extraction at configurable sample rates (0.5-30 FPS)
- Audio extraction at 16kHz mono WAV format
- Video metadata generation

✅ **Audio Transcription**

- Whisper-powered audio-to-text transcription
- Configurable model sizes (tiny, base, small, medium, large)
- Word-level and character-level timestamp options

✅ **Web Interface**

- Drag & drop video upload
- Real-time processing status updates
- Results gallery with metadata, transcription, and frames
- Download processed files

✅ **REST API**

- Asynchronous job processing
- Status polling
- File downloads

---

## 🚀 Quick Start

### Windows

```bash
# Run the batch file
quickstart.bat

# Terminal 1: Start backend
python app.py

# Terminal 2: Start frontend
cd frontend
npm start
```

### Mac/Linux

```bash
# Make script executable
chmod +x quickstart.sh
./quickstart.sh

# Terminal 1: Start backend
python app.py

# Terminal 2: Start frontend
cd frontend
npm start
```

**Then open** [http://localhost:3000](http://localhost:3000)

---

## 📦 Prerequisites

### System Requirements

- **Python**: 3.8 or higher
- **Node.js**: LTS version (for frontend)
- **FFmpeg**: System-level installation (not via pip)

### Install System Dependencies

#### Windows

1. **FFmpeg**: Download from https://ffmpeg.org/download.html
   - Extract and add `bin` folder to System PATH
   - Verify: `ffmpeg -version`

2. **Python**: Download from https://www.python.org/

3. **Node.js**: Download from https://nodejs.org/

#### Mac (using Homebrew)

```bash
brew install ffmpeg
brew install python
brew install node
```

#### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install ffmpeg python3 python3-pip nodejs npm
```

---

## 💾 Installation

### Step 1: Backend Setup

```bash
# Navigate to project root
cd Video-Compliance-Framework

# Install Python dependencies
pip install -r requirements.txt
```

**Dependencies include:**

- opencv-python (video processing)
- numpy (numerical computing)
- flask (web framework)
- flask-cors (cross-origin support)
- faster-whisper (audio transcription)
- gunicorn (production server)

### Step 2: Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install
```

**Dependencies include:**

- React & React DOM (UI library)
- Axios (HTTP client)
- Lucide React (icons)
- React Router (navigation)

---

## ▶️ Running the Application

### Development Mode

**Terminal 1 - Backend Server:**

```bash
python app.py
```

Expected output:

```
* Running on http://0.0.0.0:5000
* WARNING: This is a development server...
Press CTRL+C to quit
```

**Terminal 2 - Frontend Development Server:**

```bash
cd frontend
npm start
```

The app will automatically open at [http://localhost:3000](http://localhost:3000)

### Production Mode

**Backend:**

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**Frontend:**

```bash
cd frontend
npm run build
# Serve the build folder with a static server
```

---

## 📚 Project Structure

```
Video-Compliance-Framework/
├── app.py                      # Flask backend server
├── VideoPreprocessor.py        # Video frame & audio extraction
├── AudioToText.py              # Audio transcription module
├── ocr.py                      # OCR utilities
├── requirements.txt            # Python dependencies
├── uploads/                    # Uploaded video storage
├── preprocessed_output/        # Processing results
├── frontend/
│   ├── src/
│   │   ├── App.js             # Main React component
│   │   ├── components/        # React components
│   │   │   ├── VideoUploader.js
│   │   │   ├── ProcessingStatus.js
│   │   │   └── ResultsDisplay.js
│   │   ├── index.js
│   │   └── App.css
│   ├── public/
│   └── package.json
└── documentation/
    ├── SETUP_GUIDE.md         # Detailed setup instructions
    ├── BACKEND_API.md         # API endpoint documentation
    ├── SYSTEM_EXPLANATION.md  # System architecture
    ├── QUICKSTART.md          # Quick start guide
    └── TRANSCRIPTION_OPTIMIZATION.md
```

---

## 🔌 API Endpoints

### POST /api/process-video

**Upload and process a video**

**Request (multipart/form-data):**

```
video:        (file) - Video file to process
sampleFps:    (number, default: 2) - Frames per second to extract
modelSize:    (string, default: base) - Whisper model size
wordLevel:    (boolean, default: false) - Include word timestamps
```

**Response (202 Accepted):**

```json
{
  "jobId": "d1a2b3c4-e5f6-7a8b-9c0d-e1f2g3h4i5j6",
  "message": "Video processing started"
}
```

### GET /api/job-status/{jobId}

**Check processing status and retrieve results**

**Response:**

```json
{
  "status": "completed",
  "progress": 100,
  "message": "Processing complete",
  "data": {
    "duration": 22.86,
    "originalFps": 29.97,
    "sampleFps": 2.0,
    "frames": [
      {
        "frame_id": 0,
        "timestamp_sec": 0.0,
        "file_path": "/path/to/frame_00000.png"
      }
    ],
    "transcription": "Full transcribed text...",
    "audioPath": "/path/to/audio.wav",
    "metadataPath": "/path/to/metadata.json",
    "framesZipPath": "/path/to/frames.zip"
  }
}
```

**Status States:**

- `pending` - Job queued
- `processing` - Currently processing (includes progress 0-100)
- `completed` - Successfully finished with results
- `error` - Failed with error message

### GET /api/download

**Download processed files**

**Query Parameters:**

```
file: <path>  - Relative path to file
```

**Example:**

```
GET /api/download?file=preprocessed_output/job-id/frames.zip
```

---

## 🎬 Supported Video Formats

- `.mp4` (H.264, H.265)
- `.mov` (Apple ProRes, H.264)
- `.mkv` (Matroska)
- `.avi` (Windows Video)
- `.webm` (VP8, VP9)

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
FLASK_ENV=development
FLASK_DEBUG=True
API_HOST=0.0.0.0
API_PORT=5000
UPLOAD_FOLDER=uploads
OUTPUT_FOLDER=preprocessed_output
MAX_FILE_SIZE=5368709120
```

### Video Processing Parameters

| Parameter   | Range                            | Default | Description                   |
| ----------- | -------------------------------- | ------- | ----------------------------- |
| `sampleFps` | 0.5-30                           | 2       | Frames extracted per second   |
| `modelSize` | tiny, base, small, medium, large | base    | Whisper transcription model   |
| `wordLevel` | true/false                       | false   | Include word-level timestamps |

---

## 🔍 Module Reference

### VideoPreprocessor.py

Extracts frames and audio from video files.

**Usage:**

```python
from VideoPreprocessor import preprocess_video

result = preprocess_video(
    video_path="video.mp4",
    output_base_dir="preprocessed_output",
    sample_fps=2
)

print(result.frames)        # List of frame info
print(result.audio_path)    # Path to extracted audio
print(result.metadata_path) # Path to metadata.json
```

### AudioToText.py

Transcribes audio using Whisper model.

**Usage:**

```python
from AudioToText import transcribe_audio

result = transcribe_audio(
    audio_path="audio.wav",
    model_size="base",
    word_level=False
)

print(result.full_text)  # Complete transcription
```

---

## 📖 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Get running in 30 seconds
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Complete setup for all platforms
- **[BACKEND_API.md](BACKEND_API.md)** - Detailed API documentation
- **[SYSTEM_EXPLANATION.md](SYSTEM_EXPLANATION.md)** - Architecture and design
- **[TRANSCRIPTION_OPTIMIZATION.md](TRANSCRIPTION_OPTIMIZATION.md)** - Audio transcription tuning
- **[frontend/README.md](frontend/README.md)** - Frontend features and usage

---

## 🐛 Troubleshooting

| Issue                           | Solution                                                        |
| ------------------------------- | --------------------------------------------------------------- |
| `FFmpeg not found`              | Install FFmpeg and add to PATH, then restart terminal           |
| `ModuleNotFoundError`           | Run `pip install -r requirements.txt`                           |
| `npm command not found`         | Install Node.js from https://nodejs.org/                        |
| `Port 5000/3000 already in use` | Change `API_PORT` in `.env` or kill existing process            |
| `Video upload fails`            | Check file size (max 5GB), format, and permissions              |
| `Transcription errors`          | Ensure audio is valid WAV format, check Whisper model downloads |

---

## 📋 Quick Checklist

- [ ] Python 3.8+ installed (`python --version`)
- [ ] Node.js and npm installed (`node -v`, `npm -v`)
- [ ] FFmpeg installed and in PATH (`ffmpeg -version`)
- [ ] Python dependencies installed (`pip install -r requirements.txt`)
- [ ] Frontend dependencies installed (`npm -C frontend install`)
- [ ] Video file in supported format
- [ ] Ports 5000 and 3000 are available

---

## 📄 License

See [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Please ensure:

- Code follows project conventions
- All dependencies are in `requirements.txt`
- Frontend dependencies are in `frontend/package.json`
- Documentation is updated with significant changes
