# Virtual TV Simulator

A game-like virtual TV interface for testing the Phillips Universal Remote Control.

## Features

- **Visual TV Display**: See a realistic TV screen that responds to remote commands
- **Real-time Status**: Monitor TV state (power, volume, channel, etc.)
- **Button Feedback**: Visual feedback when buttons are pressed
- **Multiple Apps**: Simulate streaming services (YouTube, Netflix, etc.)
- **Menu System**: Navigate through TV menus and settings
- **Keyboard Testing**: Test buttons directly with keyboard shortcuts (no remote program needed!)
- **Standalone Test Mode**: Run `test_standalone.py` for automated testing

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

### Using pip (Alternative)

1. Install Python 3.7 or higher
2. Install dependencies:
```bash
pip install -r requirements.txt
```

On Windows, you may also need to install pywin32:
```bash
pip install pywin32
```

## Usage

### Start the Simulator

**With Poetry:**
```bash
poetry run web-server        # Web 3D/VR simulator
poetry run desktop-simulator # Desktop 2D simulator
```

**With pip:**
```bash
python web_server.py  # Web 3D/VR simulator
python main.py        # Desktop 2D simulator
```

The virtual TV window will open and wait for commands from the remote control program.

### Run with Remote Control

1. Start the simulator first (run `python main.py`)
2. In another terminal, build and run the remote control program with simulator support:
```bash
make clean
make SIMULATOR=1
./bin/remote_control
```

Or on Windows:
```bash
make clean
make SIMULATOR=1
bin\remote_control.exe
```

### Controls

- **ESC**: Exit the simulator
- **Keyboard Shortcuts**: Test buttons directly! See `KEYBOARD_SHORTCUTS.md` for full list
  - **P** = Power, **U/D** = Volume, **M** = Mute, **H** = Home, **N** = Menu, etc.
- The TV responds to all remote control button presses via IPC

## How It Works

The simulator uses IPC (Inter-Process Communication) to receive commands from the C program:

- **Windows**: Named pipes (`\\.\pipe\phillips_remote_tv`)
- **Unix/Linux**: Unix domain sockets (`/tmp/phillips_remote_tv.sock`)

When you press a button in the remote control program, it sends the button code to the simulator, which updates the TV display accordingly.

## Troubleshooting

### Simulator doesn't receive commands

1. Make sure the simulator is running before starting the remote control program
2. Check that the remote control was built with `SIMULATOR=1`
3. On Windows, ensure you have administrator privileges if needed for named pipes

### Import errors

- Install missing dependencies: `pip install -r requirements.txt`
- On Windows, you may need: `pip install pywin32`

### Connection errors

- Close and restart both programs
- On Unix, check that `/tmp/phillips_remote_tv.sock` doesn't exist from a previous run

