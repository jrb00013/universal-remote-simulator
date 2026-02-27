# TV Simulator Streaming API

## Overview

The TV Simulator now includes a streaming API that allows you to capture and retrieve frames from the TV screen in real-time. This is useful for testing, monitoring, or integrating with external systems.

## API Endpoints

### 1. Get Current Frame (PNG)
```bash
curl http://localhost:5000/api/frame -o frame.png
```

Returns the current TV screen frame as a PNG image.

### 2. Get Current Frame (JSON)
```bash
curl http://localhost:5000/api/frame?format=json | jq
```

Returns frame data as JSON with base64-encoded image:
```json
{
  "frame": "iVBORw0KGgoAAAANSUhEUgAA...",
  "timestamp": 1234567890.123,
  "width": 512,
  "height": 512,
  "format": "png"
}
```

### 3. Get Current Frame (JPEG)
```bash
curl http://localhost:5000/api/frame?format=jpeg -o frame.jpg
```

Returns frame as JPEG (requires Pillow: `pip install Pillow`).

### 4. Get Frame Metadata
```bash
curl http://localhost:5000/api/frame/info
```

Returns frame information:
```json
{
  "has_frame": true,
  "timestamp": 1234567890.123,
  "width": 512,
  "height": 512,
  "format": "png",
  "age_seconds": 0.15
}
```

## How It Works

1. **Client-Side Capture**: The JavaScript client captures frames from the TV canvas every 200ms (5 FPS)
2. **WebSocket Transmission**: Frames are sent to the server via WebSocket (`frame_update` event)
3. **Server Storage**: The server stores the latest frame in memory
4. **API Access**: REST endpoints serve the stored frame to clients

## Testing

### Quick Test
```bash
# Run the test script
./test_simulator/test_streaming_api.sh
```

### Manual Testing
```bash
# Get a single frame
curl http://localhost:5000/api/frame -o test.png

# Check frame info
curl http://localhost:5000/api/frame/info

# Get frame as JSON
curl http://localhost:5000/api/frame?format=json

# Continuous capture (5 frames)
for i in {1..5}; do
  curl http://localhost:5000/api/frame -o "frame_$i.png"
  sleep 0.5
done
```

## Integration Examples

### Python
```python
import requests
import base64
from PIL import Image
import io

# Get frame as PNG
response = requests.get('http://localhost:5000/api/frame')
with open('frame.png', 'wb') as f:
    f.write(response.content)

# Get frame as JSON and decode
response = requests.get('http://localhost:5000/api/frame?format=json')
data = response.json()
img_data = base64.b64decode(data['frame'])
img = Image.open(io.BytesIO(img_data))
img.save('decoded_frame.png')
```

### JavaScript/Node.js
```javascript
const axios = require('axios');
const fs = require('fs');

// Get frame as PNG
axios.get('http://localhost:5000/api/frame', {
  responseType: 'arraybuffer'
}).then(response => {
  fs.writeFileSync('frame.png', response.data);
});

// Get frame info
axios.get('http://localhost:5000/api/frame/info')
  .then(response => {
    console.log('Frame info:', response.data);
  });
```

## Performance Notes

- **Frame Rate**: Frames are captured at ~5 FPS (every 200ms) to avoid overloading the server
- **Memory**: Latest frame only is stored (not a buffer)
- **Format**: Default is PNG (512x512 pixels)
- **Latency**: Frame age is typically < 1 second

## Requirements

- **Basic**: Works out of the box with PNG format
- **JPEG Support**: Install Pillow: `pip install Pillow`
- **Server**: Must be running (`poetry run web-server` or `python web_server.py`)
- **Client**: Browser must be connected to capture frames

## Troubleshooting

### No frames available
- Ensure the browser is connected to the TV simulator
- Check that the TV is powered on
- Verify WebSocket connection is active

### JPEG format not working
- Install Pillow: `pip install Pillow`
- Check server logs for errors

### Frame is black
- TV might be powered off
- Check TV state: `curl http://localhost:5000/api/state`

## API Status Codes

- `200`: Success
- `400`: Bad request
- `500`: Server error
- `501`: Feature not available (e.g., JPEG without Pillow)

