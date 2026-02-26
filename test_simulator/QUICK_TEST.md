# Quick Test Guide - Interactive 3D TV Simulator

## 🚀 Quick Start Test

### Step 1: Start the Web Server
```bash
cd test_simulator
poetry install  # If not already done
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

### Step 2: Open in Browser
Open `http://localhost:5000` in your browser.

**What to verify:**
- ✅ 3D scene loads (TV, remote, room)
- ✅ No console errors (press F12 to check)
- ✅ Status panel shows on right side
- ✅ Controls help shows on bottom left
- ✅ Remote control is visible in front of camera

### Step 3: Test 3D Remote Control
**Click buttons on the 3D remote:**
- ✅ Click Power button (red button on top)
- ✅ See IR signal beam travel from remote to TV
- ✅ Button lights up green when clicked
- ✅ TV screen updates (turns on/off)
- ✅ Status panel updates

**Test other buttons:**
- Volume Up/Down buttons
- Channel Up/Down buttons
- Home button
- Number pad (1-9)

### Step 4: Test Camera Controls
- ✅ **Mouse drag**: Rotate camera around TV
- ✅ **Scroll wheel**: Zoom in/out
- ✅ **Press 1**: Front view
- ✅ **Press 2**: Side view
- ✅ **Press 3**: Top view
- ✅ **Press 4**: Remote close-up
- ✅ **Space**: Reset camera

### Step 5: Test C Program Integration
**In a new terminal:**
```bash
cd ..
make clean
make SIMULATOR=1 WEB=1
./bin/remote_control  # or bin\remote_control.exe on Windows
```

**What to verify:**
- ✅ C program connects to web server
- ✅ Press buttons in C program menu
- ✅ See IR signals in 3D scene
- ✅ See button highlights on remote
- ✅ TV state updates in real-time

### Step 6: Run Automated Tests
**In a new terminal:**
```bash
cd test_simulator
poetry run python test_interactive_3d.py
```

**Expected output:**
- ✅ All tests pass
- ✅ Server connection works
- ✅ REST API works
- ✅ WebSocket works
- ✅ State consistency verified

## 🐛 Troubleshooting

### Scene doesn't load
- Check browser console (F12) for errors
- Verify Three.js library loads
- Check WebSocket connection

### Buttons don't work
- Check WebSocket connection status
- Verify server is running
- Check browser console for errors

### IR signals don't appear
- Verify button was actually pressed
- Check console for errors
- Try clicking different buttons

### C program can't connect
- Verify web server is running
- Check firewall settings
- Verify build used `WEB=1` flag

## ✅ Success Criteria

All features working:
- [x] 3D scene renders correctly
- [x] Remote control is clickable
- [x] IR signals appear on button press
- [x] TV screen updates
- [x] Camera controls work
- [x] C program integration works
- [x] All button codes work
- [x] State updates in real-time

## 📊 Test Results

After running all tests, you should see:
- ✅ Server Connection: PASS
- ✅ REST API: PASS
- ✅ WebSocket: PASS
- ✅ State Consistency: PASS
- ✅ All Buttons: PASS

If all tests pass, the simulator is fully functional! 🎉

