# Virtual TV Simulator

A game-like virtual TV interface for testing the Phillips Universal Remote Control. Features both a web-based 3D/VR simulator and a desktop 2D simulator.

## Quick Start

```bash
# Install dependencies
poetry install

# Start web server (3D/VR)
poetry run web-server
# Then open: http://localhost:5000

# Or start desktop simulator (2D)
poetry run desktop-simulator
```

## Documentation

- **[SETUP.md](SETUP.md)** - Complete setup instructions for all platforms
- **[FEATURES.md](FEATURES.md)** - Detailed feature documentation
- **[API.md](API.md)** - REST API and WebSocket documentation
- **[TESTING.md](TESTING.md)** - Testing guides and procedures

## Features

- **Visual TV Display**: See a realistic TV screen that responds to remote commands
- **Real-time Status**: Monitor TV state (power, volume, channel, etc.)
- **Button Feedback**: Visual feedback when buttons are pressed
- **Multiple Apps**: Simulate streaming services (YouTube, Netflix, etc.)
- **Keyboard Testing**: Test buttons directly with keyboard shortcuts
- **3D/VR Experience**: Immersive web-based 3D interface with VR-like controls

## Installation

### Using Poetry (Recommended)

1. Install [Poetry](https://python-poetry.org/) if not already installed
2. Install dependencies:
   ```bash
   poetry install
   ```
3. Run the simulator:
   ```bash
   poetry run web-server        # Web 3D/VR simulator
   poetry run desktop-simulator # Desktop 2D simulator
   ```

See [SETUP.md](SETUP.md) for detailed setup instructions.

## Usage

### Start the Simulator

**Web Server (3D/VR):**
```bash
poetry run web-server
```
Then open: **http://localhost:5000**

**Desktop Simulator (2D):**
```bash
poetry run desktop-simulator
```

### Run with Remote Control

1. Start the simulator first
2. Build the remote control with simulator support:
   ```bash
   make clean
   make SIMULATOR=1 WEB=1  # For web server
   # OR
   make SIMULATOR=1         # For desktop simulator
   ```
3. Run the remote control:
   ```bash
   ./bin/remote_control
   ```

### Keyboard Shortcuts

Test buttons directly without the remote control program:
- **P** = Power, **U/D** = Volume, **M** = Mute
- **H** = Home, **N** = Menu, **B** = Back
- **1-9** = Channel numbers
- **Y** = YouTube, **T** = Netflix, **A** = Amazon Prime
- **ESC** = Exit simulator

See [FEATURES.md](FEATURES.md) for complete keyboard shortcuts.

## How It Works

The simulator uses IPC (Inter-Process Communication) to receive commands from the C program:

- **Windows**: Named pipes (`\\.\pipe\phillips_remote_tv`)
- **Unix/Linux**: Unix domain sockets (`/tmp/phillips_remote_tv.sock`)
- **Web Server**: HTTP REST API and WebSocket connections

When you press a button in the remote control program, it sends the button code to the simulator, which updates the TV display accordingly.

## Architecture

- **Web Server**: Flask + SocketIO for 3D/VR interface
- **Desktop Simulator**: Pygame-based 2D interface
- **IPC Integration**: Cross-platform communication with C program
- **Real-time Updates**: WebSocket for instant state synchronization

## Documentation

- **[SETUP.md](SETUP.md)** - Setup instructions, troubleshooting, platform-specific guides
- **[FEATURES.md](FEATURES.md)** - All features, animations, UI elements, keyboard shortcuts
- **[API.md](API.md)** - REST API endpoints, WebSocket events, integration examples
- **[TESTING.md](TESTING.md)** - Testing procedures, automated tests, verification steps

## Troubleshooting

See [SETUP.md](SETUP.md) for detailed troubleshooting guide.

Quick fixes:
- **Import errors**: Use Poetry: `poetry install`
- **Connection errors**: Make sure simulator is running before remote control
- **Port conflicts**: Check if port 5000 is available
- **WSL/Linux errors**: Use Poetry instead of pip (see SETUP.md)

## Comparison: Web vs Desktop

| Feature | Web (3D) | Desktop (Pygame) |
|---------|----------|------------------|
| 3D Graphics | ✅ Yes | ❌ 2D only |
| VR-like Experience | ✅ Yes | ❌ No |
| Browser Access | ✅ Yes | ❌ No |
| Cross-platform | ✅ Yes | ✅ Yes |
| Performance | ⚠️ Depends on browser | ✅ Native |
| Installation | ✅ None needed | ⚠️ Python + pygame |

Choose the web version for the immersive 3D/VR experience!
