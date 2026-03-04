# Virtual TV Simulator

A game-like virtual TV interface for testing the Phillips Universal Remote Control, with **keyword-based brand detection**, **autonomous scheduling**, and a **rule-based IR protocol classifier**. Web-based 3D/VR and desktop 2D simulators.

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

- **[SETUP.md](SETUP.md)** - Setup (Poetry, platforms, troubleshooting)
- **[FEATURES.md](FEATURES.md)** - Features (3D/VR, keyboard, APIs)
- **[API.md](API.md)** - REST and WebSocket API reference
- **[docs/SERVICE_AND_AUTOMATION.md](docs/SERVICE_AND_AUTOMATION.md)** - Remote as a service (auth, webhooks, MQTT, OpenAPI) and smart home TV automation (Broadlink, Samsung, LG, CEC adapters; scheduler targets)
- **[docs/HOME_ASSISTANT_NODE_RED.md](docs/HOME_ASSISTANT_NODE_RED.md)** - Home Assistant and Node-RED integration examples
- **[PRODUCTION.md](PRODUCTION.md)** - Production deployment: env vars, security checklist, logging, graceful shutdown, Docker, Gunicorn
- **[TESTING.md](TESTING.md)** - Manual testing guide
- **[README_TESTS.md](README_TESTS.md)** - Pytest test suite
- **Full index:** [../docs/README.md](../docs/README.md)

## Features

- **Visual TV Display**: See a realistic TV screen that responds to remote commands
- **Real-time Status**: Monitor TV state (power, volume, channel, etc.)
- **Button Feedback**: Visual feedback when buttons are pressed
- **Multiple Apps**: Simulate streaming services (YouTube, Netflix, etc.)
- **Keyboard Testing**: Test buttons directly with keyboard shortcuts
- **3D/VR Experience**: Immersive web-based 3D interface with VR-like controls. Detailed room: furniture, plants, wall art, clock, thermostat, smart speaker, smart plugs, ambient strip, accent chair, media console; all smart devices (lamps, strip, plugs, hub, thermostat, candle, bulbs) react to the remote (TV state).
- **Brand detection**: `POST /api/detect-brand` with `{"text": "I have a Samsung TV"}`. Text is matched against a fixed keyword table (BRAND_KEYWORDS in `brand_detection.py`); returns `brand`, `brand_id` (C `tv_brand_t`), `confidence`. Simulator state stores `detected_brand` / `detected_brand_id`.
- **Remote as a service**: Optional API key auth, webhooks (with retry), MQTT publish and command subscribe. Endpoints: `GET /api/health`, `GET /api/state`, `POST /api/button`, `GET /api/presets`, `POST /api/preset/<name>/trigger`, `GET /api/backends`, `GET /api/backends/status`, `POST /api/backends/broadlink/learn`. OpenAPI spec at `/api/openapi` and `/api/openapi.yaml`. See [docs/SERVICE_AND_AUTOMATION.md](docs/SERVICE_AND_AUTOMATION.md) and [docs/HOME_ASSISTANT_NODE_RED.md](docs/HOME_ASSISTANT_NODE_RED.md).
- **Autonomous scheduler**: Run `poetry run python scheduler.py` with the web server up. Reads `autonomous_config.json`: time rules (e.g. 19:00, days) and presets (button_code + delay_ms). Optional **target** per rule or preset: `simulator` (default), or a named device from `service_config.json` (e.g. Broadlink, Samsung TV). Configurable `check_interval_sec`; retries on send failure; structured logging. See [docs/SERVICE_AND_AUTOMATION.md](docs/SERVICE_AND_AUTOMATION.md).
- **IR protocol from timings**: `ir_synthetic.py` produces pulse-length lists (µs) using NEC/RC5/RC6 constants from the C code. `protocol_classifier.py` identifies protocol by comparing the first pulse/space to 9ms/4.5ms (NEC), 2.66ms/889µs (RC6), or repeated 889µs (RC5), with 40% tolerance. Run `python ir_synthetic.py` to write `ir_dataset_synthetic.json` (used by the classifier or anything else that consumes timing + label).

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

### Graphics preset (runtime simulation)

The 3D simulator uses a **GPU-based graphics preset** so quality matches your hardware:

- **Server** (at startup / first request): Detects GPU name and VRAM, classifies tier (VRAM + resolution), maps to a preset (shadow quality, texture sizes, fog, particle count, pixel ratio).
- **Page load**: Preset is injected into the page as `window.GRAPHICS_PRESET` and applied in `initScene()`, `createRoom()`, and `addAmbientEffects()`.
- **WebSocket**: On connect and on `request_state`, the server emits `graphics_preset` so the client can show the active tier and stay in sync.
- **Resize**: `onWindowResize()` re-applies the preset pixel ratio so the cap is kept at runtime.
- **UI**: The status overlay shows **Graphics:** with the tier (and GPU name when available).
- **API**: `GET /api/graphics-preset` returns the current preset; `GET /api/graphics-preset?refresh=1` recomputes (auto-update).

So the runtime simulation is fully wired: detection → tier → preset → renderer, shadows, textures, fog, particles, and UI.

## Architecture

- **Web Server**: Flask + SocketIO for 3D/VR interface
- **Desktop Simulator**: Pygame-based 2D interface
- **IPC Integration**: Cross-platform communication with C program
- **Real-time Updates**: WebSocket for instant state synchronization
- **Graphics (GPU preset)**: Server detects GPU (name + VRAM), classifies tier (ULTRA/HIGH/MEDIUM/LOW/SIM_SAFE), and injects a graphics preset into the 3D simulator. The simulator applies it at runtime (renderer, shadows, textures, fog, particles). Preset is sent on page load, on WebSocket connect, and via `GET /api/graphics-preset` (use `?refresh=1` to recompute). The status overlay shows the active tier.

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
| 3D Graphics | Yes | 2D only |
| VR-like Experience | Yes | No |
| Browser Access | Yes | No |
| Cross-platform | Yes | Yes |
| Performance | Depends on browser | Native |
| Installation | None needed | Python + pygame |

Choose the web version for the immersive 3D/VR experience!
