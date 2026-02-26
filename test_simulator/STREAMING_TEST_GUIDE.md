# 📺 Streaming Services Direct Testing Guide

## Quick Test

### Step 1: Start Web Server
```bash
cd test_simulator
poetry run web-server
```

### Step 2: Open Browser
Open `http://localhost:5000` in your browser

### Step 3: Run Automated Test
In a **new terminal**:
```bash
cd test_simulator
python test_streaming_auto.py
```

Or use the simple test:
```bash
python test_streaming_simple.py
```

## Manual Testing

### Test Each Streaming Service:

1. **YouTube (Red)**
   - Click YouTube button on 3D remote (or use C program)
   - Screen should turn **RED** (#FF0000)
   - App name shows "YouTube"
   - Smooth color transition animation

2. **Netflix (Dark Red)**
   - Click Netflix button
   - Screen should turn **DARK RED** (#E50914)
   - App name shows "Netflix"
   - Color smoothly transitions from previous app

3. **Amazon Prime (Blue)**
   - Click Amazon Prime button
   - Screen should turn **BLUE** (#00A8E1)
   - App name shows "Amazon Prime"
   - Smooth cross-fade animation

4. **HBO Max (Purple)**
   - Click HBO Max button
   - Screen should turn **PURPLE** (#800080)
   - App name shows "HBO Max"
   - Color interpolation animation

## What to Verify

### Visual Checks:
- ✅ Screen color changes to service-specific color
- ✅ Smooth color transition (no sudden jumps)
- ✅ App name displays correctly
- ✅ Notification shows "Opening [Service]..."
- ✅ Status panel updates
- ✅ IR signal appears when button pressed
- ✅ Button highlights on remote

### Animation Checks:
- ✅ Cross-fade between apps (1 second)
- ✅ Color interpolation is smooth
- ✅ Text fades in/out
- ✅ No stuttering or glitches

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

## Test from C Program

```bash
# Build with simulator support
make clean
make SIMULATOR=1 WEB=1

# Run remote control
./bin/remote_control

# In menu, select option 1: "Demo Streaming Services"
```

## Expected Behavior

1. **Power must be ON** - Services only work when TV is powered on
2. **Color Changes** - Screen background changes to service color
3. **Smooth Transitions** - Colors blend smoothly between services
4. **Notifications** - "Opening [Service]..." appears
5. **State Updates** - Status panel shows current app
6. **Animations** - Cross-fade animation plays (1 second)

## Troubleshooting

### Services don't switch
- Check TV is powered on
- Verify button codes are correct
- Check browser console for errors
- Verify server is receiving button presses

### Colors don't change
- Check app name in status panel
- Verify screen brightness is > 0
- Check browser console for errors
- Try refreshing the page

### Animations don't work
- Check browser supports canvas
- Verify JavaScript is enabled
- Check console for errors
- Try different browser

## Success Criteria

✅ All 4 streaming services switch correctly
✅ Colors match expected values
✅ Smooth animations between services
✅ Notifications appear
✅ Status panel updates
✅ IR signals visible
✅ No errors in console

---

**Ready to test!** Run the automated test or test manually in the browser.

