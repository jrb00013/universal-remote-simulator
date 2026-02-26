# Quick Start Guide - Virtual TV Simulator

## Step 1: Install Poetry (if not installed)

**WSL/Linux/Mac:**
```bash
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"
```

**Windows:**
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

## Step 2: Install Dependencies

```bash
cd test_simulator
poetry install
```

**Note:** Poetry automatically handles all dependencies, including platform-specific ones (like pywin32 on Windows). No pip needed!

## Step 3: Start the Simulator

```bash
poetry run desktop-simulator
```

**Or:**
```bash
poetry run python main.py
```

**Using Poetry shell (optional):**
```bash
poetry shell
python main.py  # Now you can run directly
```

The virtual TV window will open and wait for commands.

## Step 3: Build Remote Control with Simulator Support

In the project root directory:

```bash
make clean
make SIMULATOR=1
```

## Step 4: Run the Remote Control

**Windows:**
```bash
bin\remote_control.exe
```

**Unix/Linux/Mac:**
```bash
./bin/remote_control
```

## Step 5: Test It!

1. In the remote control program, select option 2 (Demo Basic Controls)
2. Press Power - the TV should turn on!
3. Try Volume Up/Down - see the volume bar change
4. Try Channel Up/Down - see the channel number change
5. Try option 1 (Streaming Services) - see apps open on the TV

## Troubleshooting

**"Simulator not found" error:**
- Make sure the simulator is running before starting the remote control
- Check that you built with `SIMULATOR=1`

**Import errors in Python:**
- Use Poetry: `poetry install` (handles everything automatically)
- If you see "externally-managed-environment" error, Poetry is the solution!

**Connection errors:**
- Close both programs and restart them
- Make sure only one simulator instance is running

## Features to Try

- **Power Button**: Turn TV on/off with smooth animation
- **Volume Controls**: See real-time volume bar
- **Channel Numbers**: Enter channels with number pad
- **Streaming Apps**: Open YouTube, Netflix, etc.
- **Menu System**: Navigate through TV menus
- **Status Panel**: Monitor all TV state on the right side

Enjoy testing your remote control!

