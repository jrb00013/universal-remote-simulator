# 🚀 START HERE - Quick Run Guide

## Prerequisites: Install Poetry (Required!)

**Why Poetry?** Modern Linux systems (Ubuntu 23.04+, Debian 12+) block direct `pip install` to protect system Python. Poetry creates isolated virtual environments automatically.

**Windows (PowerShell):**
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

**WSL/Linux/Mac:**
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

**Verify installation:**
```bash
poetry --version
```

If not found, add Poetry to PATH:
```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="$HOME/.local/bin:$PATH"
source ~/.bashrc  # or restart terminal
```

---

## Option 1: Web 3D/VR Simulator (Recommended - Most Immersive!)

### Step 1: Install Dependencies with Poetry
```bash
cd test_simulator
poetry install
```

### Step 2: Start the Web Server
```bash
poetry run python web_server.py
```

**Or use the Poetry script:**
```bash
poetry run web-server
```

You should see:
```
============================================================
  Virtual TV Simulator - Web Server
============================================================

Starting web server...
Access the 3D TV interface at: http://localhost:5000
```

### Step 3: Open in Browser
Open your web browser and go to:
```
http://localhost:5000
```

**That's it!** You'll see a **fully interactive 3D experience** with:
- 🎮 **3D Remote Control** - Click buttons directly on the remote!
- 📡 **Visual IR Signals** - See IR beams travel from remote to TV
- ✨ **Button Animations** - Watch buttons light up when pressed
- 🎥 **Multiple Camera Views** - Press 1-4 for different perspectives
- 🌟 **Immersive Effects** - Realistic lighting, shadows, and particles

### Step 4: Connect Remote Control
In a **new terminal**, build and run:
```bash
cd ..
make clean
make SIMULATOR=1 WEB=1
./bin/remote_control
```
(On Windows: `bin\remote_control.exe`)

**The remote will automatically connect to the web server!** Press buttons in the remote control program - watch them appear in the 3D TV!

**Note:** The remote control program will automatically try to connect to the simulator when it starts. If the simulator isn't running, you'll see a warning but the program will continue.

---

## Option 2: Desktop Simulator (2D Pygame)

### Step 1: Install Dependencies with Poetry
```bash
cd test_simulator
poetry install
```

### Step 2: Run Simulator
```bash
poetry run python main.py
```

**Or use the Poetry script:**
```bash
poetry run desktop-simulator
```

A window will open with the virtual TV!

### Step 3: Use Keyboard Shortcuts
- **P** = Power
- **U** = Volume Up
- **D** = Volume Down
- **M** = Mute
- **↑/↓** = Channel Up/Down
- **H** = Home
- **N** = Menu
- **ESC** = Exit

### Step 4: Connect Remote Control
In a **new terminal**:
```bash
cd ..
make clean
make SIMULATOR=1
./bin/remote_control
```

**The remote will automatically connect to the simulator!** Press buttons in the remote control program - watch them appear in the TV window!

**Note:** The remote control program will automatically try to connect to the simulator when it starts. If the simulator isn't running, you'll see a warning but the program will continue.

---

## 🎮 Quick Test Commands

### Test Web Server from Browser Console
1. Open http://localhost:5000
2. Press F12 to open browser console
3. Type:
```javascript
socket.emit('button_press', {button_code: 0x10}); // Power button
```

### Test Web Server via REST API
```bash
curl -X POST http://localhost:5000/api/button -H "Content-Type: application/json" -d "{\"button_code\":16}"
```

Or use PowerShell:
```powershell
Invoke-RestMethod -Uri http://localhost:5000/api/button -Method POST -ContentType "application/json" -Body '{"button_code":16}'
```

---

## 📋 Troubleshooting

### "externally-managed-environment" error (WSL/Linux)
**This is why we use Poetry!** Modern Linux blocks direct pip install.

**Solution:**
```bash
# Install Poetry (if not installed)
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"

# Then use Poetry
cd test_simulator
poetry install
poetry run web-server
```

### "Module not found" errors
```bash
cd test_simulator
poetry install
```

### Poetry not found
Install Poetry first (see Prerequisites above), then:
```bash
poetry --version  # Verify installation
poetry install    # Install dependencies
```

### Still trying to use pip?
**Don't!** Always use Poetry:
- ❌ `pip install flask` → ✅ `poetry add flask` (or just `poetry install`)
- ❌ `pip install -r requirements.txt` → ✅ `poetry install`

### Using Poetry shell (optional)
Activate Poetry's virtual environment:
```bash
poetry shell
# Now you can run commands directly:
python web_server.py
python main.py
```

### Port 5000 already in use
Change the port in `web_server.py`:
```python
socketio.run(app, host='0.0.0.0', port=5001, ...)  # Change 5000 to 5001
```

### Web server won't start
- Check if Flask is installed: `pip install flask flask-socketio`
- Check Python version: `python --version` (needs 3.7+)

### Browser shows blank screen
- Check browser console (F12) for errors
- Make sure JavaScript is enabled
- Try a different browser (Chrome, Firefox, Edge)

### C program can't connect
- Make sure web server is running FIRST
- Check you built with: `make SIMULATOR=1 WEB=1`
- On Windows, check firewall settings

---

## 🎯 What You Should See

### Web 3D Simulator:
- 3D TV model in center
- Virtual room with walls, floor, ceiling
- Status panel on right side
- Controls info on bottom left
- Smooth camera movement when you drag mouse

### Desktop Simulator:
- 2D TV screen
- Status panel on right
- Instructions at bottom
- Keyboard shortcuts work immediately

---

## ⚡ Fastest Way to Test

**Just want to see it work? Run this:**

```bash
# Terminal 1: Install and start web server
cd test_simulator
poetry install
poetry run web-server

# Terminal 2: Test it (in browser)
# Open: http://localhost:5000
```

**That's it!** No build needed, no C program needed - just Poetry and a browser!

---

## 📞 Need Help?

- Check `test_simulator/README.md` for detailed docs
- Check `test_simulator/WEB_README.md` for web server info
- Check `test_simulator/TEST_REPORT.md` for testing info

---

## 🧪 Testing the Interactive 3D Simulator

### Quick Test
1. Start web server: `cd test_simulator && poetry run web-server`
2. Open browser: `http://localhost:5000`
3. Click buttons on the 3D remote control
4. Watch IR signals travel from remote to TV!
5. Test camera controls (mouse drag, zoom, press 1-4 for presets)

### Automated Testing
Run the comprehensive test suite:
```bash
cd test_simulator
poetry run python test_interactive_3d.py
```

This will test:
- ✅ Server connection
- ✅ REST API endpoints
- ✅ WebSocket communication
- ✅ State consistency
- ✅ All button codes

### Integration Test with C Program
1. Start web server (Terminal 1): `poetry run web-server`
2. Build and run remote (Terminal 2): `make SIMULATOR=1 WEB=1 && ./bin/remote_control`
3. Press buttons in C program - see them in 3D!

## 🎉 Enjoy Your Virtual TV!

The simulator is ready to use. Pick an option above and start testing!

**New Features:**
- 🎮 **Interactive 3D Remote** - Click buttons directly!
- 📡 **Visual IR Signals** - See IR beams in real-time
- ✨ **Button Animations** - Watch buttons light up
- 🎥 **Multiple Camera Views** - Press 1-4 for different perspectives
- 🌟 **Fully Immersive** - Realistic 3D environment

