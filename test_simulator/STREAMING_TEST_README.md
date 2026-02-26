# 📺 Streaming Services Direct Testing

## Quick Start

### 1. Start the Web Server
```bash
cd test_simulator
poetry run web-server
```

### 2. Open Browser
Open `http://localhost:5000` in your browser

### 3. Run Automated Test
In a **new terminal**:
```bash
cd test_simulator
poetry run python test_streaming_simple.py
```

## What Was Added

### ✅ Streaming Service Buttons on 3D Remote
The 3D remote now has 4 streaming service buttons at the bottom:
- **YT** (YouTube) - Red button
- **NF** (Netflix) - Dark red button  
- **PR** (Amazon Prime) - Blue button
- **HB** (HBO Max) - Purple button

### ✅ Test Scripts
- `test_streaming_simple.py` - Quick automated test
- `test_streaming_auto.py` - Full automated test with detailed output
- `test_streaming.py` - Interactive test with options

## Manual Testing Steps

1. **Open Browser**: `http://localhost:5000`
2. **Turn TV ON**: Click the red Power button on the 3D remote
3. **Test YouTube**: Click the **YT** button (red) at bottom of remote
   - Screen should turn **RED** (#FF0000)
   - App name shows "YouTube"
4. **Test Netflix**: Click the **NF** button (dark red)
   - Screen should turn **DARK RED** (#E50914)
   - App name shows "Netflix"
5. **Test Amazon Prime**: Click the **PR** button (blue)
   - Screen should turn **BLUE** (#00A8E1)
   - App name shows "Amazon Prime"
6. **Test HBO Max**: Click the **HB** button (purple)
   - Screen should turn **PURPLE** (#800080)
   - App name shows "HBO Max"

## Expected Behavior

✅ **Color Changes**: Screen background changes to service-specific color
✅ **Smooth Transitions**: Colors blend smoothly between services (1 second cross-fade)
✅ **Notifications**: "Opening [Service]..." appears briefly
✅ **Status Panel**: Shows current app name
✅ **IR Signals**: Red beam appears when button pressed
✅ **Button Highlights**: Remote buttons glow when clicked

## Button Codes

- **YouTube**: 0x01
- **Netflix**: 0x02
- **Amazon Prime**: 0x03
- **HBO Max**: 0x04

## Test from Browser Console

Open browser console (F12) and run:

```javascript
// Test YouTube
socket.emit('button_press', {button_code: 0x01});

// Test Netflix
socket.emit('button_press', {button_code: 0x02});

// Test Amazon Prime
socket.emit('button_press', {button_code: 0x03});

// Test HBO Max
socket.emit('button_press', {button_code: 0x04});
```

## Automated Test Output

When you run `test_streaming_simple.py`, you should see:

```
============================================================
STREAMING SERVICES TEST
============================================================

[OK] Server connected

Testing streaming services:

-> YouTube... [PASS]
-> Netflix... [PASS]
-> Amazon Prime... [PASS]
-> HBO Max... [PASS]

[OK] Test complete! Check the browser to see the animations.
```

## Troubleshooting

### Server not running
- Make sure you started: `poetry run web-server`
- Check port 5000 is not in use
- Look for errors in server terminal

### Services don't switch
- TV must be powered ON first
- Check browser console for errors
- Verify button codes are correct

### Colors don't change
- Check app name in status panel
- Verify screen brightness > 0
- Try refreshing the page

## Success Criteria

✅ All 4 streaming services switch correctly
✅ Colors match expected values:
   - YouTube: #FF0000 (Red)
   - Netflix: #E50914 (Dark Red)
   - Amazon Prime: #00A8E1 (Blue)
   - HBO Max: #800080 (Purple)
✅ Smooth animations between services
✅ Notifications appear
✅ Status panel updates
✅ IR signals visible
✅ No errors in console

---

**Ready to test!** Start the server, open the browser, and click the streaming buttons on the 3D remote!

