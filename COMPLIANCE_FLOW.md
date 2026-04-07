# Video Compliance Framework - Complete Flow

This document describes the integrated compliance analysis flow of the Video Compliance Framework.

## Overview

The framework provides an end-to-end video compliance analysis system that performs the following operations:

1. **Video Upload/Processing** - Extract frames and audio from video
2. **Audio Transcription** - Convert audio to text using Whisper
3. **Optical Character Recognition (OCR)** - Extract text from video frames
4. **Logo Detection** - Identify logos/brands using YOLO
5. **Transcript Validation** - Check transcription against compliance rules
6. **Report Generation** - Produce comprehensive compliance report

---

## Processing Pipeline

### Step 1: Video Upload & Frame/Audio Extraction

**Input:** Video file (MP4, MOV, MKV, AVI, WebM)  
**Module:** `VideoPreprocessor.py`

The system:

- Extracts frames at configurable sample rate (0.5-30 FPS)
- Extracts audio at 16kHz mono WAV
- Preserves temporal information (timestamps)

**Output:**

- Frame images with metadata
- Audio WAV file
- Duration and FPS information

---

### Step 2: Audio Transcription

**Input:** Extracted audio file  
**Module:** `AudioToText.py` (Whisper-based)

The system:

- Transcribes audio to text
- Supports multiple model sizes (tiny, base, small, medium, large-v3)
- Optional word-level timestamps

**Parameters:**

- `modelSize`: Size/accuracy tradeoff (tiny = fast, large-v3 = accurate)
- `wordLevel`: Include word-by-word timestamps

**Output:**

- Full transcription text
- Optional word-level timing information

---

### Step 3: Optical Character Recognition (OCR)

**Input:** Frame images  
**Module:** `ocr.py`

The system:

- Uses EasyOCR for text detection in images
- Processes sample frames for performance
- Extracts visible text (signage, overlays, captions)

**Features:**

- Light preprocessing (upscaling)
- Fallback mechanisms
- Garbage text filtering

**Output:**

- Detected text per frame
- Frame IDs and timestamps
- Text summary

---

### Step 4: Logo Detection

**Input:** Frame images  
**Module:** `logo_detect.py` (YOLO-based)

The system:

- Uses fine-tuned YOLOv8 model (`best.pt`)
- Detects brand logos/specific visual elements
- Samples frames for efficiency

**Features:**

- Confidence scoring
- Temporal tracking
- Detection frequency analysis

**Output:**

- Logo detections with confidence levels
- Frame locations and timestamps
- Detection frequency report

---

### Step 5: Compliance Rules Checking

**Input:** Full transcription text  
**Module:** `TranscriptValidator.py` + custom rules

The system checks for:

- **Prohibited terms** - Words/phrases not allowed
- **Warning terms** - Terms that require review
- **Length validation** - Minimum content requirements
- **Structure validation** - Proper formatting

**Compliance Rules:**

```
- Prohibited words: ['explicit', 'banned', 'violate']
- Warning words: ['caution', 'warning']
- Minimum word count: 10
- Score calculation:
  - -20 per prohibited term
  - -5 per warning term
  - -3 if too short
```

**Output:**

- Compliance score (0-100)
- Issues found
- Warnings
- Pass/Fail status

---

### Step 6: Comprehensive Report Generation

**Input:** All analysis results  
**Module:** Custom report generator

The system generates a report containing:

1. **Video Analysis**
   - Duration, FPS, frame count
   - Video quality metrics

2. **Text Analysis (OCR)**
   - Detected text samples
   - Number of frames with text
   - Text frequency

3. **Logo Analysis**
   - Number of logos detected
   - Confidence levels
   - Detection timeline

4. **Compliance Status**
   - Transcript validation result
   - Compliance score
   - Issues and warnings
   - Violations found

5. **Overall Status**
   - PASSED: Score ≥ 80, no issues
   - REVIEW_REQUIRED: Score 60-80 or suspicious logos
   - FAILED: Score < 60 or issues found

**Output:**

- JSON report
- PDF export (optional)
- Actionable insights

---

## API Endpoints

### POST /api/process-video

Process a video file through the complete pipeline.

**Request:**

```
Form Data:
- video: Video file
- sampleFps: Frame sampling rate (0.5-30)
- modelSize: Whisper model (tiny, base, small, medium, large-v3)
- wordLevel: Word-level timestamps (true/false)
```

**Response (202 Accepted):**

```json
{
  "jobId": "uuid",
  "message": "Processing started"
}
```

### GET /api/job-status/{jobId}

Check processing status.

**Response:**

```json
{
  "status": "completed|processing|error",
  "progress": 85,
  "message": "Step 5/7: Processing frames...",
  "data": {
    "duration": 120.5,
    "frames": [...],
    "transcription": "...",
    "compliance_report": {
      "overall_status": "PASSED",
      "overall_score": 92,
      "video_analysis": {...},
      "text_analysis": {...},
      "logo_analysis": {...},
      "compliance": {...}
    }
  }
}
```

---

## Frontend Components

### ProcessingStatus.js

Displays real-time processing progress with 7 steps:

1. Extracting frames and audio
2. Transcribing audio
3. Performing OCR on frames
4. Detecting logos
5. Checking compliance rules
6. Preparing frames
7. Generating report

### ResultsDisplay.js

Displays results in tabs:

- **Metadata** - Video information
- **Transcription** - Full transcribed text
- **Frames** - Frame gallery with preview
- **Compliance Report** - Full analysis report
- **Downloads** - Export options

---

## Configuration & Customization

### Compliance Rules

Edit compliance rules in `app.py` function `check_compliance_rules()`:

```python
prohibited_words = ['explicit', 'banned', 'violate']
warning_words = ['caution', 'warning']
```

### OCR Settings

Edit in `ocr.py`:

- Image preprocessing (upscaling factor)
- OCR Engine selection (EasyOCR vs Tesseract)
- Sample frame selection

### Logo Detection

Edit in `logo_detect.py`:

- YOLO model confidence threshold (default: 0.5)
- Frame sampling rate
- Detection classes

### Report Scoring

Edit in `app.py` function `generate_compliance_report()`:

- Score thresholds
- Status determination logic
- Weighted metrics

---

## Performance Optimization

### For Faster Processing

1. Use "Tiny" model: ~5-10s per minute
2. Lower sample FPS: 1-2 fps
3. Reduce frame OCR sampling
4. Skip logo detection for non-brand videos

### For Better Accuracy

1. Use "Large" model: ~60-120s per minute
2. Higher sample FPS: 5-10 fps
3. Process all frames for OCR
4. Enable word-level timestamps

### Resource Requirements

| Component        | GPU         | CPU      | RAM  |
| ---------------- | ----------- | -------- | ---- |
| Video Processing | Optional    | 4+ cores | 4GB+ |
| Whisper (tiny)   | Optional    | 4+ cores | 2GB  |
| Whisper (large)  | Recommended | 8+ cores | 8GB+ |
| YOLO Detection   | Recommended | 4+ cores | 4GB+ |
| OCR              | Optional    | 4+ cores | 2GB  |

---

## Output Files

For each video processing job:

```
preprocessed_output/{job_id}/
├── frames/
│   ├── frame_00000.png
│   ├── frame_00001.png
│   └── ...
├── frames.zip
├── audio/
│   └── audio.wav
├── metadata.json
└── compliance_report.json
```

---

## Error Handling

### Module Failures

The system gracefully handles module failures:

- **OCR unavailable**: Skips text extraction
- **YOLO model missing**: Skips logo detection
- **Transcription error**: Returns error message
- **Processing error**: Returns detailed error code

### Fallback Strategies

1. Thumbnail generation fails → Use API path
2. OCR fails on frame → Continue to next frame
3. Logo detection fails → Continue processing
4. Transcription times out → Use shorter audio segments

---

## Future Enhancements

1. **Multi-language support** - OCR and transcription in multiple languages
2. **Custom compliance rules** - User-defined rule sets
3. **Historical comparisons** - Track compliance trends
4. **Automated actions** - Email alerts, automatic approvals
5. **Advanced filtering** - Search/filter reports by criteria
6. **Batch processing** - Process multiple videos
7. **Model training** - Fine-tune models on custom data
8. **Real-time monitoring** - Live stream compliance checking

---

## Troubleshooting

### "Module not found" errors

→ Install missing dependencies: `pip install -r requirements.txt`

### "YOLO model not found"

→ Ensure `best.pt` is in project root. Download from: [YOLOv8 model path]

### "Transcription timeout"

→ Use smaller model (tiny/base) or shorter video

### "OCR not detecting text"

→ Check image quality, try adjusting preprocessing in `ocr.py`

### "Processing too slow"

→ Reduce sample FPS, use smaller models, enable GPU acceleration

---

## API Rate Limits

- Max file size: 5GB
- Max concurrent jobs: Limited by available resources
- Max processing time: 10 minutes (configurable)
- Min FPS: 0.5
- Max FPS: 30

---

## Support & Documentation

- **README.md** - Project overview and installation
- **SETUP_GUIDE.md** - Detailed setup instructions
- **BACKEND_API.md** - Full API documentation
- **SYSTEM_EXPLANATION.md** - System architecture
- **TROUBLESHOOTING.md** - Common issues and solutions
- **COMPLIANCE_FLOW.md** - This document

---

## License

MIT License - See LICENSE file for details
