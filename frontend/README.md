# Video Compliance Framework - Frontend

A modern React-based frontend for the Video Compliance Framework that allows users to upload videos, extract frames and audio, and download transcriptions.

## Features

- 🎥 **Video Upload** - Drag & drop or click to upload video files
- 📹 **Supported Formats** - MP4, MOV, MKV, AVI, WebM
- ⚙️ **Configurable Settings** - Adjust frame sampling rate and transcription model size
- 📊 **Metadata Display** - View video duration, FPS, and frame information
- 📝 **Audio Transcription** - Powered by Whisper model with word-level timestamps
- 🖼️ **Frame Gallery** - Browse extracted frames with timestamps
- ⬇️ **Download Options** - Export transcription, audio, frames, and metadata

## Project Structure

```
frontend/
├── public/
│   └── index.html          # HTML entry point
├── src/
│   ├── components/         # React components
│   │   ├── VideoUploader.js
│   │   ├── VideoUploader.css
│   │   ├── ProcessingStatus.js
│   │   ├── ProcessingStatus.css
│   │   ├── ResultsDisplay.js
│   │   └── ResultsDisplay.css
│   ├── App.js             # Main app component
│   ├── App.css            # App styles
│   ├── index.js           # React entry point
│   └── index.css          # Global styles
├── package.json           # Dependencies
├── .env.example           # Environment variables template
└── README.md             # This file
```

## Installation

### Prerequisites

- Node.js 14.0 or higher
- npm or yarn package manager
- Backend API running (see backend setup)

### Steps

1. **Clone and navigate to frontend directory**

   ```bash
   cd Video-Compliance-Framework/frontend
   ```

2. **Install dependencies**

   ```bash
   npm install
   ```

3. **Configure environment variables**

   ```bash
   cp .env.example .env.local
   # Edit .env.local and set REACT_APP_API_URL to your backend URL
   ```

4. **Start development server**
   ```bash
   npm start
   ```

The app will open at `http://localhost:3000`

## Environment Variables

Create a `.env.local` file in the frontend directory:

```env
# Backend API URL
REACT_APP_API_URL=http://localhost:5000
```

## Backend API Integration

The frontend expects the following API endpoints from your backend:

### 1. **Process Video**

- **Endpoint:** `POST /api/process-video`
- **Accepts:** Multipart form-data with video file and settings
- **Parameters:**
  - `video` (file) - Video file to process
  - `sampleFps` (number) - Frames to extract per second
  - `modelSize` (string) - Whisper model size (tiny, base, small, medium, large-v3)
  - `wordLevel` (boolean) - Enable word-level timestamps
- **Returns:** `{ jobId, id }`

### 2. **Job Status**

- **Endpoint:** `GET /api/job-status/:jobId`
- **Returns:** `{ status, progress, message, data }`
- **Status values:** pending, processing, completed, error
- **Data on completion:**
  ```json
  {
    "duration": 120.5,
    "originalFps": 30,
    "sampleFps": 2,
    "frames": [
      {
        "frame_id": 0,
        "timestamp_sec": 0.0,
        "file_path": "path/to/frame_0.png"
      }
    ],
    "transcription": "[00:00:00 - 00:00:05] Sample text here...",
    "audioPath": "path/to/audio.wav",
    "framesZipPath": "path/to/frames.zip"
  }
  ```

### 3. **Download File**

- **Endpoint:** `GET /api/download?file=path/to/file`
- **Returns:** File download

## Usage

1. **Upload Video**
   - Drag and drop a video file or click to browse
   - Select processing settings (frame rate, model size, options)
   - Click "Process Video"

2. **View Progress**
   - Real-time progress bar and status updates
   - Check processing steps being executed

3. **View Results**
   - **Metadata Tab:** Video information and statistics
   - **Transcription Tab:** Full transcribed text with timestamps
   - **Frames Tab:** Gallery of extracted frames
   - **Downloads Tab:** Export all data

4. **Download Results**
   - Download transcription as TXT
   - Download extracted audio as WAV
   - Download all frames as ZIP
   - Download metadata as JSON
   - Copy transcription to clipboard

## API Response Example

After successful processing, the frontend receives:

```json
{
  "status": "completed",
  "data": {
    "duration": 120.5,
    "originalFps": 30,
    "sampleFps": 2,
    "frames": [
      {
        "frame_id": 0,
        "timestamp_sec": 0.0,
        "file_path": "/path/to/preprocessed_output/frames/frame_0.png",
        "preview": "base64_encoded_preview"
      }
    ],
    "transcription": "[00:00:00 - 00:00:05] Hello world...",
    "audioPath": "/path/to/preprocessed_output/audio.wav"
  }
}
```

## Component Architecture

### VideoUploader

- Handles file selection and drag-drop
- Configurable processing settings
- File validation and size checking

### ProcessingStatus

- Real-time progress visualization
- Step-by-step status tracking
- Error handling and display

### ResultsDisplay

- Tabbed interface for different result types
- Frame gallery with timestamps
- Download functionality for all outputs
- Transcription copy-to-clipboard

## Development

### Available Scripts

```bash
# Start development server
npm start

# Build for production
npm build

# Run tests
npm test

# Eject configuration (one-way operation)
npm run eject
```

### Customization

- **Colors:** Modify gradient colors in CSS files (currently purple/blue theme)
- **API URL:** Set `REACT_APP_API_URL` environment variable
- **File Limits:** Adjust in `VideoUploader.js` (currently 5GB)
- **Polling Interval:** Modify in `VideoUploader.js` (currently 1 second)

## Troubleshooting

### "API Connection Failed"

- Ensure backend is running at the configured URL
- Check `REACT_APP_API_URL` in `.env.local`
- Verify backend CORS settings

### "Unsupported Format"

- Ensure video is in: MP4, MOV, MKV, AVI, or WebM
- Check file extension is correct

### "Processing Timeout"

- Processing took longer than 5 minutes
- Try with smaller video or lower model size
- Check backend logs for errors

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (responsive design)

## License

See LICENSE file in the main project directory.

## Backend Documentation

For backend setup and API details, see the main [README.md](../README.md)
