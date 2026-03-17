# Audio Transcription Speed Optimization Guide

## ⚡ Quick Speed Comparison

| Model           | Speed       | Accuracy  | RAM   | First Download |
| --------------- | ----------- | --------- | ----- | -------------- |
| **tiny** ⚡     | 5-10s/min   | Good      | 1GB   | ~40MB          |
| **base**        | 10-20s/min  | Better    | 1.5GB | ~140MB         |
| **small**       | 20-30s/min  | High      | 2.5GB | ~465MB         |
| **medium**      | 40-60s/min  | Very High | 5GB   | ~1.5GB         |
| **large-v3** 🐢 | 60-120s/min | Best      | 10GB  | ~2.9GB         |

**Recommended:** `tiny` for speed, `base` for balanced accuracy/speed

---

## 🚀 Speed Optimization Methods

### 1. **Use Faster Model (Easiest)**

In the frontend, select **"Tiny"** model:

- ⚡ 10x faster than base
- 🎯 Still accurate enough for most use cases
- 💾 Only downloads 40MB

### 2. **Enable GPU Acceleration (Best Performance)**

**Check if you have CUDA-capable GPU:**

```powershell
# Check for NVIDIA GPU
nvidia-smi

# If available, install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**Speed improvement with GPU:**

- CPU (tiny model): ~10s per minute
- GPU (tiny model): ~2-3s per minute ⚡

---

## 📊 Real-World Examples

### 5-minute video:

- **tiny model (CPU):** ~50-60 seconds
- **tiny model (GPU):** ~10-15 seconds ✨
- **base model (CPU):** ~100 seconds
- **base model (GPU):** ~20-30 seconds

### 30-minute video:

- **tiny model (CPU):** ~5-10 minutes
- **tiny model (GPU):** ~1-2 minutes ✨
- **base model (CPU):** ~10-20 minutes
- **base model (GPU):** ~2-5 minutes

---

## 🔧 Backend Configuration Options

### Current Setup (Optimized):

```python
# app.py - Uses 'tiny' model by default
optimized_model = 'tiny' if model_size == 'base' else model_size
```

### Manual Model Selection:

User can select from frontend dropdown:

- Tiny (Recommended) ⚡
- Base (Balanced)
- Small, Medium, Large (More accurate)

---

## 💡 Best Practices

### For Quick Transcription:

1. ✅ Select **Tiny model** in frontend
2. ✅ Ensure FFmpeg is installed (critical)
3. ✅ Use **GPU if available** (install CUDA PyTorch)
4. ✅ Update ffmpeg: `ffmpeg -version` should show recent date

### For Higher Accuracy:

1. ✅ Select **Base or Small model**
2. ✅ Enable GPU acceleration helps a lot
3. ✅ Ensure sufficient RAM (8GB+ recommended)

### For Production:

1. ✅ Use **GPU server** (AWS GPU instance, etc.)
2. ✅ Deploy with Docker for consistency
3. ✅ Use **base model** for good balance
4. ✅ Implement result caching (same videos processed once)
5. ✅ Use load balancing for multiple requests

---

## 🐛 Troubleshooting

### Transcription Still Slow?

**Check 1: Verify Model Size Selected**

```powershell
# In Backend logs, you should see:
# 📊 Using model: tiny
# 🎙️ Using device: GPU or CPU
```

**Check 2: Verify FFmpeg Works**

```powershell
ffmpeg -version
```

Should show recent version. If missing:

- **Windows:** Download from https://ffmpeg.org/download.html
- **Mac:** `brew install ffmpeg`
- **Linux:** `sudo apt install ffmpeg`

**Check 3: Check Available RAM**

```powershell
# Windows - Check Task Manager (Ctrl+Shift+Esc)
# Should have 4GB+ free

# Or use PowerShell:
Get-ComputerInfo | Select CsSystemFreePhysicalMemory
```

**Check 4: Verify GPU (if installed)**

```powershell
pip list | find "torch"

# Should show cuda or gpu in version info
# If not, install with CUDA support:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

---

## 🎯 Quick Optimization Checklist

- [ ] Using **Tiny** model (selected in frontend)
- [ ] FFmpeg installed and working (`ffmpeg -version`)
- [ ] At least 4GB RAM available
- [ ] Audio file is valid WAV format (16kHz mono)
- [ ] Backend shows "device: GPU" in logs (optional but fast)
- [ ] Check internet connection for first model download

---

## 📥 First Download Times

First time using a model, it downloads from Hugging Face:

| Model    | Download Size | Time (~)      |
| -------- | ------------- | ------------- |
| tiny     | 40MB          | 10-30 seconds |
| base     | 140MB         | 30-60 seconds |
| small    | 465MB         | 1-2 minutes   |
| medium   | 1.5GB         | 3-5 minutes   |
| large-v3 | 2.9GB         | 5-10 minutes  |

**After first run:** Cached locally, no download needed

---

## 🔄 Model Cache Location

Models are cached at:

- **Windows:** `C:\Users\<username>\AppData\Local\.cache\huggingface`
- **Mac:** `~/.cache/huggingface`
- **Linux:** `~/.cache/huggingface`

To clear cache (if needed):

```powershell
# Windows
Remove-Item -Path "$env:USERPROFILE\.cache\huggingface" -Recurse -Force

# Mac/Linux
rm -rf ~/.cache/huggingface
```

---

## 📈 Performance Tips

### Batch Processing

If processing multiple videos:

1. Process smallest to largest (tiny models first)
2. Enable GPU (huge speedup)
3. Pre-cache models (run one "tiny" first)

### Server Deployment

```bash
# Install faster-whisper with GPU support
pip install faster-whisper[cuda]

# Run with Gunicorn + multiple workers
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker (For Consistency)

```dockerfile
FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y python3 ffmpeg
RUN pip install faster-whisper torch
```

---

## 📚 Additional Resources

- [faster-whisper GitHub](https://github.com/guillaumekln/faster-whisper)
- [Whisper Model Sizes](https://openai.com/index/whisper/)
- [PyTorch CUDA Installation](https://pytorch.org/get-started/locally/)

---

## 💬 Summary

**To speed up transcription:**

1. ⚡ **Select "Tiny" model** (default now) - 10x faster
2. 🎮 **Install CUDA PyTorch** - 3-5x faster on GPU
3. 🔧 **Ensure FFmpeg installed** - Critical for audio
4. 💾 **Check available RAM** - At least 4GB

**Expected speeds (with Tiny model):**

- Single CPU: ~10 seconds per minute of audio
- GPU: ~2-3 seconds per minute of audio ✨

Good luck! 🚀
