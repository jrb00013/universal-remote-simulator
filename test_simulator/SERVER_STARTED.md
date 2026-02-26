# 🚀 Server Started!

## Status: RUNNING

The Virtual TV Simulator web server has been started!

## Access the 3D TV

Open your web browser and navigate to:

```
http://localhost:5000
```

You should see:
- A 3D TV model in a virtual room
- Status panel on the right
- Controls info on the bottom left
- Smooth camera movement (drag mouse to rotate)

## Controls

- **Mouse Drag**: Rotate camera around TV
- **Scroll Wheel**: Zoom in/out
- **Space**: Reset camera position
- **ESC**: Exit (in browser, not server)

## Test the TV

### From Browser Console (F12):
```javascript
socket.emit('button_press', {button_code: 0x10}); // Power button
socket.emit('button_press', {button_code: 0x11}); // Volume Up
socket.emit('button_press', {button_code: 0x14}); // Channel Up
```

### Via REST API:
```bash
curl -X POST http://localhost:5000/api/button -H "Content-Type: application/json" -d "{\"button_code\":16}"
```

## Server Management

### Stop the Server
Press `Ctrl+C` in the terminal where the server is running.

### Restart the Server
```bash
cd test_simulator
poetry run web-server
```

### Check if Server is Running
```bash
# Windows PowerShell
Get-NetTCPConnection -LocalPort 5000

# Linux/Mac
netstat -an | grep 5000
# or
lsof -i :5000
```

## Troubleshooting

### Can't connect to server
- Make sure server is running (check terminal)
- Check if port 5000 is available
- Try http://127.0.0.1:5000 instead

### Browser shows blank screen
- Check browser console (F12) for errors
- Make sure JavaScript is enabled
- Try a different browser

### Server won't start
- Check if port 5000 is already in use
- Make sure dependencies are installed: `poetry install`
- Check Python version (3.7+ required)

## Next Steps

1. **Open browser**: http://localhost:5000
2. **Test buttons**: Use browser console or connect C program
3. **Enjoy**: Experience the 3D/VR TV simulator!

The server is running and ready to use! 🎉

