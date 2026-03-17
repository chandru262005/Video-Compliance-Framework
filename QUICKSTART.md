# QUICK START GUIDE

## 🚀 30-Second Setup

### Windows

1. Double-click `quickstart.bat`
2. Wait for installation to complete
3. Run Command Prompt:
   ```
   python app.py
   ```
4. In another Command Prompt:
   ```
   cd frontend
   npm start
   ```
5. Open http://localhost:3000

### Mac/Linux

1. Open Terminal and run:
   ```bash
   chmod +x quickstart.sh
   ./quickstart.sh
   ```
2. In Terminal 1:
   ```bash
   python app.py
   ```
3. In Terminal 2:
   ```bash
   cd frontend
   npm start
   ```
4. Open http://localhost:3000

---

## What You Get

✅ **Frontend** (React)

- Video upload with drag & drop
- Real-time processing status
- Metadata, transcription, and frame gallery
- Download results (transcription, audio, frames, metadata)

✅ **Backend** (Python/Flask)

- Video frame extraction
- Audio extraction and processing
- Whisper-based transcription
- REST API with job status tracking

✅ **Integrated Workflow**

- Video → Frames + Audio
- Audio → Transcription
- All results downloadable

---

## 📚 Full Documentation

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Detailed setup for all platforms
- **[BACKEND_API.md](BACKEND_API.md)** - API endpoints and usage
- **[frontend/README.md](frontend/README.md)** - Frontend features and settings
- **[README.md](README.md)** - Original project documentation

---

## ⚡ Key Features

| Feature              | Details                                       |
| -------------------- | --------------------------------------------- |
| **Video Upload**     | Drag & drop, MP4/MOV/MKV/AVI/WebM format      |
| **Frame Extraction** | Configurable sample rate (0.5-30 FPS)         |
| **Audio Processing** | 16kHz mono WAV extraction                     |
| **Transcription**    | Whisper model (tiny to large) with timestamps |
| **Results**          | Metadata, transcription, frames, audio        |
| **Downloads**        | Export TXT, WAV, ZIP, JSON                    |

---

## 🔧 System Requirements

- **Python** 3.8+
- **Node.js** 14+
- **FFmpeg** (system install)
- **RAM** 4GB minimum (8GB+ recommended)
- **GPU** Optional (CUDA for faster Whisper)

---

## 🎬 Usage Flow

```
1. Upload Video
   ↓
2. Configure Settings (FPS, Model Size)
   ↓
3. Click Process
   ↓
4. Wait for Processing (progress shown)
   ↓
5. View Results (metadata, transcription, frames)
   ↓
6. Download Files
```

---

## 🐛 Common Issues

| Issue             | Solution                                                             |
| ----------------- | -------------------------------------------------------------------- |
| Port 5000 in use  | Change port in app.py or kill process: `lsof -ti:5000 \| xargs kill` |
| CORS errors       | Backend is running on `http://localhost:5000`                        |
| Module not found  | Run `pip install -r requirements.txt`                                |
| npm install fails | Delete node_modules and .package-lock.json, try again                |
| FFmpeg not found  | Install FFmpeg and add to PATH                                       |

---

## 📞 Support

Check documentation files for:

- Detailed configuration
- API endpoint usage
- Troubleshooting guides
- Performance optimization

---

**Ready? Run `quickstart.bat` (Windows) or `./quickstart.sh` (Mac/Linux)**

Happy processing! 🎬✨
