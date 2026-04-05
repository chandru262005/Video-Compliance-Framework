# Video Compliance Framework - Complete System Explanation

## System Overview

This is a full-stack web application for video processing and analysis. It consists of:

- **Frontend**: React-based UI running on port 3000
- **Backend**: Flask API running on port 5000
- **Processing**: Python modules for video processing and transcription

---

## BACKEND (Flask API - port 5000)

### Architecture

The backend is a Flask REST API that handles video processing asynchronously using background threads.

### Core Modules

#### 1. **app.py** - Main Flask Server

The entry point that provides HTTP endpoints for the frontend.

**Key Components:**

- **CORS Enabled**: Allows requests from frontend (different port)
- **Job Tracking**: In-memory dictionary stores processing jobs
- **Background Threading**: Processes videos asynchronously

**Configuration Constants:**

```
UPLOAD_FOLDER = 'uploads'          # Where uploaded videos are stored
OUTPUT_FOLDER = 'preprocessed_output'  # Where processed files are stored
MAX_FILE_SIZE = 5GB               # File upload limit
ALLOWED_EXTENSIONS = {mp4, mov, mkv, avi, webm}
```

---

### API Endpoints

#### 1. POST `/api/process-video`

**Purpose**: Upload a video and start processing

**Request Data (multipart/form-data):**

```
video: <file>              # The video file to process
sampleFps: 2.0            # Frames per second to extract (1-30)
modelSize: "base"         # Whisper model for transcription
wordLevel: false          # Word-level timestamps in transcription
```

**Response (202 Accepted):**

```json
{
  "jobId": "uuid-string",
  "id": "uuid-string",
  "message": "Video processing started"
}
```

**Processing Steps:**

1. File validation (format, size)
2. Save file with unique ID
3. Create job entry in `jobs` dictionary
4. Start background thread to process video
5. Return job ID immediately (async response)

**What Happens in Background:**

- Extracts frames from video (using VideoPreprocessor)
- Extracts audio track from video
- Transcribes audio using Whisper (using AudioToText)
- Formats all results and stores in job

---

#### 2. GET `/api/job-status/<job_id>`

**Purpose**: Check processing status and get results

**Query Parameters:** None

**Response:**

```json
{
  "status": "pending|processing|completed|error",
  "progress": 0-100,
  "message": "Current status message",
  "data": { /* results when completed */ },
  "error": "Error message if failed"
}
```

**Status States:**

- `pending`: Job queued, waiting to start
- `processing`: Currently processing (shows progress 0-100)
- `completed`: Finished successfully with `data` field populated
- `error`: Processing failed with error message

**Response Data Structure (when completed):**

```json
{
  "duration": 22.86, // Total video duration in seconds
  "originalFps": 29.97, // Original video frame rate
  "sampleFps": 2.0, // Frames extracted per second
  "frames": [
    {
      "frame_id": 0,
      "timestamp_sec": 0.0,
      "file_path": "/path/to/frame_00000.png",
      "preview": "/path/to/frame_00000.png"
    }
    // ... more frames
  ],
  "transcription": "Full text transcript with timestamps",
  "audioPath": "/path/to/audio.wav",
  "metadataPath": "/path/to/metadata.json",
  "framesZipPath": "/path/to/frames.zip",
  "jobId": "uuid-string"
}
```

---

#### 3. GET `/api/download`

**Purpose**: Download processed files

**Query Parameters:**

```
file: <path>  // Path to file to download (relative path)
```

**Example:**

```
GET /api/download?file=preprocessed_output/job-id/frames
```

**Security:**

- Prevents directory traversal (`..` attacks)
- Only allows downloading from allowed directories

**Returns:** Binary file as attachment

---

#### 4. GET `/api/health`

**Purpose**: Health check endpoint

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2026-03-23T12:00:00.000000"
}
```

---

#### 5. GET `/`

**Purpose**: Root endpoint with API documentation

**Response:**

```json
{
  "message": "Video Compliance Framework API",
  "version": "1.0.0",
  "endpoints": {
    /* all endpoints listed */
  }
}
```

---

### Processing Pipeline (Background Job)

```
1. VALIDATION
   ├─ Check file exists
   ├─ Check file format
   └─ Check file size

2. VIDEO PREPROCESSING (VideoPreprocessor.py)
   ├─ Open video with OpenCV
   ├─ Extract frames at specified FPS
   │  ├─ Save as PNG files
   │  └─ Store crop/resize if needed
   ├─ Extract audio track
   │  └─ Convert to 16kHz mono WAV
   └─ Generate metadata.json

3. AUDIO TRANSCRIPTION (AudioToText.py)
   ├─ Load Whisper model
   ├─ Transcribe with timestamps
   └─ Generate word-level timestamps (optional)

4. RESULT ASSEMBLY
   ├─ Collect all frames
   ├─ Package transcription
   ├─ Get metadata
   └─ Store in job['data']

5. CLEANUP
   └─ Delete original uploaded video file
```

---

### Module: VideoPreprocessor.py

**Purpose**: Extract frames and audio from video

**Main Function:**

```python
preprocess_video(
    video_path: str,              # Input video file
    output_base_dir: str = "preprocessed_output",
    sample_fps: float = 2.0       # Frames per second to sample
) -> PreprocessorOutput
```

**Output Structure:**

```
{
  video_path: str,
  duration_sec: float,          # Total video length
  original_fps: float,          # Source video FPS
  sample_fps: float,            # Sample rate used
  frames: List[FrameInfo],      # List of extracted frames
  audio_path: str,              # Path to extracted audio
  metadata_path: str            # Path to metadata.json
}
```

**Key Functions:**

1. `validate_video_path()` - Check if file exists and is supported format
2. `get_video_metadata()` - Extract FPS and duration using OpenCV
3. `sample_frames()` - Extract frames at specified interval
4. `extract_audio()` - Pull audio using FFmpeg
5. `save_metadata()` - Write metadata to JSON

---

### Module: AudioToText.py

**Purpose**: Transcribe audio using OpenAI's Whisper

**Main Function:**

```python
transcribe_audio(
    audio_path: str,             # Input audio file (WAV)
    model_size: str = "tiny",    # Model size (tiny|base|small|medium|large-v3)
    word_level: bool = False     # Include word-level timestamps
) -> str
```

**Model Sizes & Speed:**

```
tiny:     ~5-10s per minute of audio   (FASTEST - recommended)
base:     ~10-20s per minute          (Good balance)
small:    ~20-30s per minute
medium:   ~40-60s per minute
large-v3: ~60-120s per minute         (MOST ACCURATE)
```

**Hardware Support:**

- Detects GPU (CUDA) automatically
- Uses float16 on GPU, int8 on CPU
- Falls back to CPU if CUDA unavailable

**Output:**

- Timestamped transcript text
- Format: `[00:00:00.000 --> 00:00:05.000] Text content...`

---

## FRONTEND (React - port 3000)

### Architecture

Single-page React application with component-based structure.

### Component Structure

```
App.js (Main Container)
├── VideoUploader.js      (File upload & settings)
├── ProcessingStatus.js   (Progress indicator)
└── ResultsDisplay.js     (Results viewer)
```

---

### 1. **App.js** - Main Container

**Purpose**: Manage overall app state and coordinate components

**State Management:**

```javascript
processingState = {
  isProcessing: boolean,    // Currently processing?
  progress: 0-100,          // Progress percentage
  currentStep: string,      // What step we're on
  error: null|string        // Error message if any
}

results = null|{...}        // Store final results
```

**Event Handlers:**

- `handleUploadStart()`: Called when user clicks Process
- `handleProcessingProgress()`: Called while processing
- `handleProcessingComplete()`: Called when done
- `handleProcessingError()`: Called if error
- `handleReset()`: Clear state for new upload

**Rendering Logic:**

```
IF not results:
  Show VideoUploader
ELSE IF results:
  Show ResultsDisplay
ELSE IF isProcessing:
  Show ProcessingStatus
```

---

### 2. **VideoUploader.js** - File Upload & Settings

**Purpose**: Accept video files and configure processing options

**Features:**

#### Drag & Drop Zone

- Click or drag to select video
- Visual feedback on hover
- Shows file name when selected
- Validates file size (max 5GB)

#### Processing Settings

**Sample FPS Slider:**

- Range: 0.5 - 30 frames per second
- Default: 2.0
- Lower = fewer frames, faster processing
- Higher = more frames, more detailed

**Transcription Model Selection:**

- tiny: Ultra-fast (5-10s/min) - Good for speed
- base: Fast (10-20s/min) - Good balance
- small: Medium (20-30s/min)
- medium: Slower (40-60s/min)
- large-v3: Very Slow (60-120s/min) - Best accuracy

**Word-level Timestamps:**

- Checkbox option
- When enabled: transcription includes word-by-word timing
- Default: disabled (takes longer, larger output)

**Supported Formats:**

```
.mp4, .mov, .mkv, .avi, .webm
```

**Process Flow:**

1. User selects video
2. Configure settings
3. Click "Process Video" button
4. File sent to backend via multipart/form-data
5. Backend returns job ID
6. Start polling job status

---

### 3. **ProcessingStatus.js** - Progress Indicator

**Purpose**: Show real-time processing progress

**Display Elements:**

#### Progress Bar

- Visual bar fills 0-100%
- Shows current percentage
- Smooth animation

#### Checkpoint List

```
Uploading video file         [✓ completed]
Extracting frames           [● current]
Extracting audio            [pending]
Transcribing audio          [pending]
Generating results          [pending]
```

**Status Indicators:**

- ✓ completed: Step finished
- ● current: Currently processing
- (empty): Waiting to start

#### Status Message

- Shows current operation
- Updates every 1 second via polling

#### Error Display

- Shows if processing fails
- Large red error box
- Displays error message

**Polling Logic:**

- Polls `/api/job-status/<job_id>` every 1 second
- Updates progress when status changes
- Shows error if status = 'error'
- Completes when status = 'completed'

---

### 4. **ResultsDisplay.js** - Results Viewer

**Purpose**: Display and download processed results

**Tab System:**

#### Tab 1: Metadata

**Shows:**

```
┌─────────────────────┐
│ Video Duration: 22.86s │
│ Original FPS: 29.97    │
│ Sample FPS: 2.0        │
│ Total Frames: 49       │
└─────────────────────┘
```

**Cards Display:**

- Duration (seconds)
- Original frame rate
- Sample frame rate
- Number of frames extracted

#### Tab 2: Transcription

**Shows:**

- Full transcript text
- Sorted chronologically
- Scrollable area (max 400px height)
- Copy button to clipboard

**Example Format:**

```
[00:00:00.000] Welcome to the video
[00:01:32.500] This is the next scene
[00:05:45.123] And so on...
```

#### Tab 3: Frames

**Shows:**

- Grid of extracted frame images
- Each frame card shows:
  - Thumbnail image
  - Frame ID (e.g., "Frame #0")
  - Timestamp (seconds with decimals)
- Clickable cards (for potential zoom)
- Responsive grid layout

#### Tab 4: Downloads

**Download Buttons:**

1. **Transcription (TXT)**
   - Downloads as text file
   - All transcript with timestamps

2. **Audio (WAV)**
   - Downloads extracted audio
   - 16kHz mono format
   - Clean audio suitable for ASR

3. **Frames (ZIP)**
   - All frames as PNG files
   - Organized in single zip
   - Easy batch processed

4. **Metadata (JSON)**
   - Processing metadata
   - Includes duration, FPS, settings
   - Useful for logging/reporting

**Button Section:**

- "Process Another Video" button
- Clears all state
- Returns to uploader

---

## DATA FLOW DIAGRAM

```
FRONTEND (React)
    │
    ├─ User selects video
    ├─ Configures settings
    └─ Clicks "Process Video"
        │
        └─► HTTP POST /api/process-video
            (multipart/form-data)
                │
                ▼
BACKEND (Flask)
    │
    ├─ Save uploaded file
    ├─ Create job entry
    ├─ Start background thread
    └─► Return job ID (202 Accepted)
        │
        ▼ [In Background Thread]
        │
        ├─ VideoPreprocessor
        │  ├─ Extract frames (PNG)
        │  └─ Extract audio (WAV)
        │
        ├─ AudioToText
        │  └─ Transcribe audio
        │
        └─ Save results to job['data']
            │
            ▼
FRONTEND (React)
    │
    ├─ Poll /api/job-status/<job_id>
    ├─ Update progress bar
    ├─ Show current step
    └─ When complete: Display results
        │
        ▼
User Views Results
    │
    ├─ View metadata
    ├─ Read transcription
    ├─ Browse frames
    └─ Download files
```

---

## Key Technologies

### Frontend

- **React 18**: UI framework
- **Axios**: HTTP requests
- **CSS3**: Styling and animations

### Backend

- **Flask**: Web framework
- **Flask-CORS**: Cross-origin requests
- **Werkzeug**: File handling

### Processing

- **OpenCV**: Video frame extraction
- **FFmpeg**: Audio extraction
- **Faster-Whisper**: Audio transcription
- **PyTorch**: GPU acceleration

---

## File Structure

```
Backend:
app.py                      # Flask API server
VideoPreprocessor.py        # Video extraction
AudioToText.py             # Audio transcription
requirements.txt           # Python dependencies

Frontend:
public/index.html          # HTML entry point
src/
  ├── App.js              # Main container
  ├── App.css             # Main styling
  ├── index.js            # React entry
  ├── index.css           # Global styles
  └── components/
      ├── VideoUploader.js
      ├── VideoUploader.css
      ├── ProcessingStatus.js
      ├── ProcessingStatus.css
      ├── ResultsDisplay.js
      └── ResultsDisplay.css
```

---

## Workflow Examples

### Example 1: Basic Video Processing

1. User drags video.mp4 onto upload area
2. Default settings: sampleFps=2, modelSize=base
3. Clicks "Process Video"
4. Backend extracts 2 frames per second
5. Extracts audio
6. Transcribes with 'base' model (10-20s per min)
7. User sees progress: 0% → 50% → 100%
8. Results displayed in tabs

### Example 2: Fast Processing (Busy User)

1. User uploads video
2. Changes modelSize to 'tiny'
3. Sets sampleFps to 1 (fewer frames)
4. Processing is much faster
5. Trade-off: Less accurate transcription, fewer frames

### Example 3: Detailed Analysis

1. User uploads video
2. Sets sampleFps to 5 (more detailed)
3. Changes modelSize to 'large-v3' (best accuracy)
4. Checks wordLevel for word timestamps
5. Processing takes longer but results are detailed

---

## Error Handling

### Frontend Errors

- File format not supported
- File size exceeds limit
- Network request failed
- Job processing failed

### Backend Errors

- Video file corrupted
- FFmpeg not installed
- Insufficient disk space
- GPU out of memory (Whisper)

### User Feedback

- Large red error box with message
- Allows user to clear and retry
- Error doesn't crash application

---

## Performance Optimization Tips

1. **Reduce Sample FPS**: Use 1 instead of 2 for faster processing
2. **Use Smaller Model**: 'tiny' is 5-10x faster than 'large-v3'
3. **GPU Support**: Install CUDA for 10-100x speedup
4. **Batch Processing**: Process multiple videos in sequence

---

## API Usage Examples

### cURL: Process Video

```bash
curl -X POST http://localhost:5000/api/process-video \
  -F "video=@video.mp4" \
  -F "sampleFps=2" \
  -F "modelSize=base" \
  -F "wordLevel=false"
```

### cURL: Check Status

```bash
curl http://localhost:5000/api/job-status/job-uuid-here
```

### JavaScript: Process Video

```javascript
const formData = new FormData();
formData.append("video", fileInput.files[0]);
formData.append("sampleFps", 2);
formData.append("modelSize", "base");

const response = await fetch("http://localhost:5000/api/process-video", {
  method: "POST",
  body: formData,
});
const { jobId } = await response.json();
```

---

## Conclusion

This system provides a complete video processing pipeline with an intuitive UI for uploading, configuring, and analyzing video content. The asynchronous design allows large files to be processed without blocking the user interface, while the modular architecture makes it easy to extend with additional features.
