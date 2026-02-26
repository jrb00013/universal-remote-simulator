# Quick Start Guide - Virtual TV Simulator

## Step 1: Install Dependencies

```bash
cd test_simulator
pip install -r requirements.txt
```

On Windows, you may also need:
```bash
pip install pywin32
```

## Step 2: Start the Simulator

**Windows:**
```bash
python main.py
```
or double-click `run_simulator.bat`

**Unix/Linux/Mac:**
```bash
python3 main.py
```
or run `./run_simulator.sh` (make it executable first: `chmod +x run_simulator.sh`)

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
- Install missing packages: `pip install -r requirements.txt`
- On Windows: `pip install pywin32`

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

