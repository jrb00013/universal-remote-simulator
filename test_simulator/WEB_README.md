# Web-Based 3D/VR Virtual TV Simulator

## 🎮 Immersive 3D Experience

This is a **web-based 3D/VR-like virtual TV simulator** that provides an immersive experience accessible through any modern web browser. It features:

- **Full 3D Environment**: Realistic 3D TV in a virtual room
- **VR-like Controls**: Smooth camera movement and rotation
- **Real-time Updates**: WebSocket connection for instant button responses
- **Cross-platform**: Works on Windows, Mac, Linux, and mobile devices
- **No Installation**: Just open in a browser!

## Quick Start

### 1. Install Poetry (if not installed)

**WSL/Linux/Mac:**
```bash
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"
```

**Windows:**
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

### 2. Install Dependencies with Poetry

```bash
cd test_simulator
poetry install
```

**Note:** Poetry automatically creates a virtual environment and handles all dependencies. No need for `pip install`!

### 3. Start the Web Server

```bash
poetry run web-server
```

**Or:**
```bash
poetry run python web_server.py
```

### 3. Open in Browser

The server will start at: **http://localhost:5000**

Open this URL in your web browser to see the 3D TV!

### 4. Connect Remote Control (Optional)

Build the remote control with web server support:

```bash
make clean
make SIMULATOR=1 WEB=1
./bin/remote_control
```

## Features

### 🎥 3D TV Model
- Realistic TV with frame, screen, and stand
- Dynamic screen content based on TV state
- Smooth power on/off animations
- Emissive screen glow when powered on

### 🏠 Immersive Room
- Virtual room environment
- Floor, walls, and ceiling
- Ambient lighting and shadows
- Subtle particle effects for atmosphere

### 🎮 VR-like Controls

**Mouse:**
- **Click & Drag**: Rotate camera around TV (orbit control)
- **Scroll Wheel**: Zoom in/out
- **Right-click**: Pan camera (if implemented)

**Keyboard:**
- **Space**: Reset camera to default position

### 📊 Real-time Status Panel
- Power status
- Volume level
- Current channel
- Active app
- Mute status
- Game mode
- Last button pressed

### 🔔 Notifications
- Visual notifications for button presses
- Appears at bottom of screen
- Auto-dismisses after 2 seconds

## Architecture

### Server (Flask + SocketIO)
- **Flask**: Web server and REST API
- **Flask-SocketIO**: WebSocket support for real-time updates
- **IPC Integration**: Can receive commands from C program via named pipes/sockets

### Client (Three.js)
- **Three.js**: 3D graphics library
- **WebSocket**: Real-time communication with server
- **Canvas API**: Dynamic screen content generation

## API Endpoints

### REST API
- `GET /api/state` - Get current TV state
- `POST /api/button` - Send button code
  ```json
  {
    "button_code": 16
  }
  ```

### WebSocket Events
- `connect` - Client connected
- `tv_state_update` - TV state changed
- `button_press` - Button pressed from client

## Button Codes

All button codes match `include/remote_buttons.h`:
- `0x10` = Power
- `0x11` = Volume Up
- `0x12` = Volume Down
- `0x13` = Mute
- `0x14` = Channel Up
- `0x15` = Channel Down
- `0x01` = YouTube
- `0x02` = Netflix
- etc.

## Testing

### Test from Browser Console

```javascript
// Send button press via WebSocket
socket.emit('button_press', {button_code: 0x10}); // Power

// Or via REST API
fetch('/api/button', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({button_code: 0x10})
});
```

### Test with C Program

1. Start web server: `poetry run web-server`
2. Build with web support: `make SIMULATOR=1 WEB=1`
3. Run: `./bin/remote_control`
4. Press buttons - see them appear in the 3D TV!

## Troubleshooting

### Server won't start
- Check if port 5000 is already in use
- Install dependencies with Poetry: `poetry install`
- Check Python version (3.7+ required)
- If you see "externally-managed-environment" error, use Poetry (see WSL_SETUP.md)

### Browser shows blank screen
- Check browser console for errors (F12)
- Ensure WebSocket connection is working
- Try refreshing the page

### C program can't connect
- Make sure web server is running first
- Check firewall settings
- Verify `WEB=1` was used when building

### Performance issues
- Use a modern browser (Chrome, Firefox, Edge)
- Reduce browser zoom level
- Close other heavy applications

## Future Enhancements

- [ ] Full WebXR/VR support
- [ ] Multiple camera angles
- [ ] Sound effects
- [ ] More detailed room decorations
- [ ] Remote control 3D model
- [ ] Screen mirroring from actual content
- [ ] Multi-user support
- [ ] Mobile device controls

## Comparison: Web vs Desktop

| Feature | Web (3D) | Desktop (Pygame) |
|---------|----------|-------------------|
| 3D Graphics | ✅ Yes | ❌ 2D only |
| VR-like Experience | ✅ Yes | ❌ No |
| Browser Access | ✅ Yes | ❌ No |
| Cross-platform | ✅ Yes | ✅ Yes |
| Performance | ⚠️ Depends on browser | ✅ Native |
| Installation | ✅ None needed | ⚠️ Python + pygame |

Choose the web version for the immersive 3D/VR experience!

