# Photo Mode Features

## Overview
The E-Paper Display now supports two distinct modes:
- **Photo Mode**: Display a single photo with automatic dithering
- **Screen Mode**: Display dynamic widgets and screens

## UI Changes

### Mode Selector
- Toggle button at the top of the UI
- Switch between Photo Mode and Screen Mode
- Automatically updates the e-paper display

### Photo Mode
- View current photo being displayed
- Upload new photos via:
  - Click to browse
  - Drag and drop
- Supported formats: JPEG, PNG, GIF, etc.
- Photos are automatically dithered to black/white/red for the e-paper display

### Screen Mode
- Select from available screens (all except photo_frame)
- Same functionality as before
- Switching screens updates the display

## API Endpoints

### Switch Mode
```bash
curl -X PUT http://localhost:8000/api/v1/mode \
     -H "Content-Type: application/json" \
     -d '{"mode": "photo"}'  # or "screen"
```

### Upload Photo
```bash
curl -X POST http://localhost:8000/api/v1/upload-photo \
     -F "file=@/path/to/image.jpg"
```

### Get Current Photo
```bash
curl http://localhost:8000/api/v1/current-photo > current-photo.jpg
```

## Technical Details

### Photo Storage
- Photos are stored in `photo/` directory
- Filename is always `image.jpg` (uploaded photos overwrite the existing one)
- PhotoWidget reads from `PHOTOS_DIR / "image.jpg"`

### Mode Switching
- Photo Mode → switches to `photo_frame` screen
- Screen Mode → switches to last used non-photo screen or defaults to `digital_clock`
- Mode state is tracked in `app.state.current_mode`

### Display Updates
- Uploading a photo in Photo Mode triggers automatic refresh
- Mode switching always performs a full screen refresh

## Usage Example

1. Start the API server:
   ```bash
   uv run python main.py
   ```

2. Open the web UI: http://localhost:8000

3. Login (if authentication is enabled)

4. Click "Photo Mode" toggle

5. Upload a photo:
   - Click the upload area
   - Or drag and drop an image
   - Photo will be displayed on the e-paper

6. Switch to "Screen Mode" to show widgets

7. Switch back to "Photo Mode" to see the photo again
