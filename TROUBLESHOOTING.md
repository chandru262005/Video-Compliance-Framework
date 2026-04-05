# Quick Start & Troubleshooting Guide

## 🚀 Starting the Application

### Step 1: Install Dependencies

**Backend:**

```bash
cd Video-Compliance-Framework
pip install -r requirements.txt
```

**Frontend:**

```bash
cd frontend
npm install
cd ..
```

### Step 2: Start Backend (Terminal 1)

```bash
python app.py
```

**Expected Output:**

```
 * Running on http://0.0.0.0:5000
 * WARNING: This is a development server. Do not use it in production.
 * Press CTRL+C to quit
```

### Step 3: Start Frontend (Terminal 2)

```bash
cd frontend
npm start
```

**Browser Window** should open at `http://localhost:3000`

---

## ✅ What Should Work Now

### 1. **File Upload**

- ✅ Drag & drop video
- ✅ Click to browse
- ✅ File validation (format & size)
- ✅ Clear error messages with suggestions

### 2. **Processing Settings**

- ✅ Sample FPS slider (0.5 - 30)
- ✅ Transcription model selection
- ✅ Word-level timestamps option
- ✅ Helpful descriptions

### 3. **Live Processing**

- ✅ Real-time progress bar
- ✅ Step-by-step status
- ✅ Elapsed time counter
- ✅ API connection indicator (top-right)

### 4. **Results Display**

- ✅ Metadata tab (duration, FPS, frame count)
- ✅ Transcription tab (full text, copy button)
- ✅ Frames tab (grid view, click to expand)
- ✅ Downloads tab (all files)

### 5. **Frame Viewing**

- ✅ Click any frame to see full-size preview
- ✅ Shows frame ID and timestamp
- ✅ Close button to return to grid

### 6. **Downloads**

- ✅ Download transcription as TXT
- ✅ Download audio as WAV
- ✅ Download all frames as ZIP
- ✅ Download metadata as JSON

---

## 🔧 Troubleshooting

### Issue: "API Status: disconnected" 🔴

**Cause**: Backend not running or wrong port

**Solutions**:

1. Check if Python process is running: `python app.py`
2. Verify Flask is installed: `pip list | grep flask`
3. Try other port:
   ```bash
   # Edit app.py, change port=5000 to port:8000
   python app.py
   # Then in frontend Terminal 2:
   export REACT_APP_API_URL=http://localhost:8000
   npm start
   ```

---

### Issue: "No file selected" Error

**Cause**: File validation failed silently

**Solutions**:

1. Check file format (MP4, MOV, MKV, AVI, WebM only)
2. Check file size (Max 5GB)
3. Try uploading different file
4. Check browser console (F12) for errors

---

### Issue: "File size exceeds 5GB limit" After Upload

**Cause**: File too large

**Solutions**:

1. Compress video: `ffmpeg -i input.mp4 -crf 23 output.mp4`
2. Split into smaller segments
3. Check file actually exists: `ls -lh video.mp4`

---

### Issue: "Processing failed" After Upload Starts

**Cause**: Backend error during processing

**Solutions**:

1. Check Terminal 1 (backend) for error messages
2. Verify FFmpeg is installed: `ffmpeg -version`
3. Check VideoPreprocessor.py for errors
4. Verify AudioToText.py is available
5. Check disk space: `df -h`

**Common Backend Errors**:

```
ModuleNotFoundError: No module named 'cv2'
→ Solution: pip install opencv-python

ModuleNotFoundError: No module named 'faster_whisper'
→ Solution: pip install faster-whisper

FFmpeg is not installed or not on your system PATH
→ Solution: Install FFmpeg (see README.md)
```

---

### Issue: "Processing timeout" After Long Wait

**Cause**: Processing took longer than 10 minutes

**Solutions**:

1. Use "Tiny" model instead of "Large"
2. Process shorter videos first
3. Try with lower sample FPS
4. Check system resources (RAM, disk)

**To increase timeout**:
Edit `frontend/src/components/VideoUploader.js`:

```javascript
const maxAttempts = 600; // 10 minutes
// Change to 1200 for 20 minutes
```

---

### Issue: Frames Not Loading in Results

**Cause**: Frame paths incorrect or images missing

**Solutions**:

1. Check backend folder: `ls -la preprocessed_output/`
2. Verify frames exist: `ls -la preprocessed_output/{jobId}/frames/`
3. Check browser console (F12) for image load errors
4. Restart backend to clear cache

---

### Issue: Transcription Shows Nothing

**Cause**: Whisper model not downloaded or audio issue

**Solutions**:

1. Model downloads on first use (might be large)
2. Check terminal for download progress
3. Try "Tiny" model first (smaller)
4. Verify audio.wav exists in output folder
5. Try different audio sample with known good audio

**Force Model Download**:

```python
from faster_whisper import WhisperModel
model = WhisperModel("base")  # Downloads model
```

---

### Issue: "Processing stuck at 45%" or Same Percentage

**Cause**: Backend thread hung or job stuck

**Solutions**:

1. Kill backend: `CTRL+C` in Terminal 1
2. Delete stuck job: `rm -rf preprocessed_output/{stuck_jobId}`
3. Restart: `python app.py`
4. Try again with different video

---

### Issue: Can't Download Files

**Cause**: Files missing or path incorrect

**Solutions**:

1. Verify files exist: `ls -la preprocessed_output/{jobId}/`
2. Check download function in DevTools
3. Check browser download settings
4. Try download with API directly:
   ```
   http://localhost:5000/api/download?file=preprocessed_output/{jobId}/audio/audio.wav
   ```

---

### Issue: Mobile View Looks Broken

**Cause**: Responsive CSS not loaded

**Solutions**:

1. Hard refresh: `CTRL+Shift+R` (Cmd+Shift+R on Mac)
2. Clear browser cache
3. Check CSS files loaded: F12 → Network tab

---

### Issue: "CORS error" in Console

**Cause**: Backend CORS not configured properly

**Solutions**:

1. Check backend Terminal 1 for CORS errors
2. Verify Flask-CORS enabled: `CORS(app, origins="*")`
3. Try accessing API directly: `http://localhost:5000/api/health`
4. Check if port changed

---

## 🧪 Testing Commands

### Test Backend API

```bash
# Check if backend is running
curl http://localhost:5000/api/health

# Expected response:
# {"status":"healthy","timestamp":"2026-04-05T..."}

# Test file upload (macOS/Linux)
curl -X POST http://localhost:5000/api/process-video \
  -F "video=@test_video.mp4" \
  -F "sampleFps=2" \
  -F "modelSize=tiny"

# Check job status
curl http://localhost:5000/api/job-status/{jobId}
```

### Test in Browser Console (F12)

```javascript
// Check API connection
fetch("http://localhost:5000/api/health")
  .then((r) => r.json())
  .then((d) => console.log(d));

// Check available frames
fetch(
  "http://localhost:5000/preprocessed_output/test-id/frames/frame_00000.png",
).then((r) => console.log(r.status));
```

---

## 📊 Performance Tips

### For Faster Processing:

1. **Use "Tiny" Model**: 5-10 seconds per minute of audio
2. **Lower Sample FPS**: Use 1-2 instead of 5-10
3. **Shorter Videos**: Start with <5 minute videos
4. **Disable Word-Level**: Unchecking saves time

### For Better Accuracy:

1. **Use "Base" or "Small" Model**: Better transcription
2. **Higher Sample FPS**: More detailed frames
3. **Longer Videos**: More data for context
4. **Clean Audio**: Remove background noise first

### For Systems with Limited Resources:

1. **Use "Tiny" Model**: Requires less RAM
2. **Process One at a Time**: Don't start multiple jobs
3. **Lower FPS**: Reduces memory usage
4. **Close Other Apps**: Free up system memory

---

## 🎯 Next Steps After Successful Run

1. **Try Different Videos**: Test with various formats
2. **Experiment with Settings**: See quality/speed tradeoffs
3. **Download Results**: Verify all files work
4. **Check Transcription**: Verify accuracy
5. **Review Frames**: Ensure sample rate is right
6. **File Issues**: If something breaks, check logs

---

## 📞 Support

### Check These First:

1. Read error message carefully
2. Check Terminal 1 (backend) logs for details
3. Try with a smaller/different video
4. Restart both backend and frontend
5. Check system resources (RAM, disk)

### If Still Stuck:

1. Check browser console (F12) for errors
2. Check backend terminal for errors
3. Verify all dependencies installed
4. Check FFmpeg is working: `ffmpeg -version`
5. Try simpler video format (MP4)
