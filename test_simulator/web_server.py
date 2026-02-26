#!/usr/bin/env python3
"""
Web Server for Virtual TV Simulator
Provides a web-based 3D/VR-like interface accessible via browser
"""

from flask import Flask, render_template, send_from_directory, request
from flask_socketio import SocketIO, emit
import threading
import time
import sys
import os

app = Flask(__name__, 
            template_folder='web_templates',
            static_folder='web_static')
app.config['SECRET_KEY'] = 'phillips_remote_tv_simulator'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory('web_static', filename)

# TV State (shared with simulator logic)
tv_state = {
    'powered_on': False,
    'volume': 50,
    'channel': 1,
    'muted': False,
    'current_app': 'Home',
    'input_source': 'HDMI 1',
    'picture_mode': 'Standard',
    'sound_mode': 'Standard',
    'game_mode': False,
    'brightness': 50,
    'backlight': 50,
    'show_menu': False,
    'show_info': False,
    'show_settings': False,
    'channel_input': '',
    'last_button': None,
    'notification': None,
}

# Button code mappings
BUTTON_CODES = {
    0x01: "YouTube", 0x02: "Netflix", 0x03: "Amazon Prime", 0x04: "HBO Max",
    0x10: "Power", 0x11: "Volume Up", 0x12: "Volume Down", 0x13: "Mute",
    0x14: "Channel Up", 0x15: "Channel Down", 0x20: "Home", 0x21: "Menu",
    0x22: "Back", 0x23: "Exit", 0x24: "Options", 0x25: "Input", 0x26: "Source",
    0x30: "Up", 0x31: "Down", 0x32: "Left", 0x33: "Right", 0x34: "OK", 0x35: "Enter",
    0x40: "Play", 0x41: "Pause", 0x42: "Stop", 0x43: "Fast Forward", 0x44: "Rewind",
    0x50: "0", 0x51: "1", 0x52: "2", 0x53: "3", 0x54: "4",
    0x55: "5", 0x56: "6", 0x57: "7", 0x58: "8", 0x59: "9", 0x5A: "Dash",
    0x60: "Red", 0x61: "Green", 0x62: "Yellow", 0x63: "Blue",
    0x70: "Info", 0x71: "Guide", 0x72: "Settings", 0x73: "CC", 0x74: "Subtitles",
    0x77: "Sleep", 0x78: "Picture Mode", 0x80: "Voice", 0x82: "Live TV", 0x83: "Stream",
    0xA0: "Game Mode", 0xB0: "Motion", 0xB1: "Backlight", 0xB2: "Brightness",
    0xC0: "Sound Mode", 0xD0: "Multi View", 0xD1: "PIP", 0xD2: "Screen Mirror",
}

def handle_button_press(button_code):
    """Handle button press and update TV state"""
    button_name = BUTTON_CODES.get(button_code, f"Unknown (0x{button_code:02X})")
    tv_state['last_button'] = button_name
    tv_state['notification'] = f"Button: {button_name}"
    
    print(f"[Web Server] Button pressed: {button_name} (0x{button_code:02X})")
    
    # Handle button actions
    if button_code == 0x10:  # Power
        tv_state['powered_on'] = not tv_state['powered_on']
        tv_state['notification'] = f"Power: {'ON' if tv_state['powered_on'] else 'OFF'}"
        print(f"[Web Server] TV Power: {'ON' if tv_state['powered_on'] else 'OFF'}")
        
        # If turning on, ensure we have a valid app/state
        if tv_state['powered_on'] and not tv_state.get('current_app'):
            tv_state['current_app'] = 'Home'
        
    elif button_code == 0x11:  # Volume Up
        if tv_state['powered_on']:
            tv_state['volume'] = min(100, tv_state['volume'] + 1)
            tv_state['notification'] = f"Volume: {tv_state['volume']}%"
            
    elif button_code == 0x12:  # Volume Down
        if tv_state['powered_on']:
            tv_state['volume'] = max(0, tv_state['volume'] - 1)
            tv_state['notification'] = f"Volume: {tv_state['volume']}%"
            
    elif button_code == 0x13:  # Mute
        if tv_state['powered_on']:
            tv_state['muted'] = not tv_state['muted']
            tv_state['notification'] = f"Mute: {'ON' if tv_state['muted'] else 'OFF'}"
            
    elif button_code == 0x14:  # Channel Up
        if tv_state['powered_on']:
            tv_state['channel'] = (tv_state['channel'] % 999) + 1
            tv_state['notification'] = f"Channel: {tv_state['channel']}"
            
    elif button_code == 0x15:  # Channel Down
        if tv_state['powered_on']:
            tv_state['channel'] = ((tv_state['channel'] - 2) % 999) + 1
            tv_state['notification'] = f"Channel: {tv_state['channel']}"
            
    elif button_code == 0x20:  # Home
        if tv_state['powered_on']:
            tv_state['current_app'] = "Home"
            tv_state['show_menu'] = False
            tv_state['show_settings'] = False
            tv_state['show_info'] = False
            
    elif button_code == 0x21:  # Menu
        if tv_state['powered_on']:
            tv_state['show_menu'] = not tv_state['show_menu']
            tv_state['show_settings'] = False
            tv_state['show_info'] = False
            
    elif button_code == 0x22:  # Back
        if tv_state['powered_on']:
            tv_state['show_menu'] = False
            tv_state['show_settings'] = False
            tv_state['show_info'] = False
    
    elif button_code == 0x25 or button_code == 0x26:  # Input / Source
        if tv_state['powered_on']:
            # Cycle through HDMI inputs
            hdmi_inputs = ['HDMI 1', 'HDMI 2', 'HDMI 3', 'HDMI 4', 'TV', 'Component', 'AV']
            current_index = hdmi_inputs.index(tv_state['input_source']) if tv_state['input_source'] in hdmi_inputs else 0
            next_index = (current_index + 1) % len(hdmi_inputs)
            tv_state['input_source'] = hdmi_inputs[next_index]
            tv_state['notification'] = f"Input: {tv_state['input_source']}"
            
    elif button_code == 0x70:  # Info
        if tv_state['powered_on']:
            tv_state['show_info'] = not tv_state['show_info']
            
    elif button_code == 0x72:  # Settings
        if tv_state['powered_on']:
            tv_state['show_settings'] = not tv_state['show_settings']
            tv_state['show_menu'] = False
            
    elif button_code == 0x01:  # YouTube
        if tv_state['powered_on']:
            tv_state['current_app'] = "YouTube"
            tv_state['notification'] = "Opening YouTube..."
            
    elif button_code == 0x02:  # Netflix
        if tv_state['powered_on']:
            tv_state['current_app'] = "Netflix"
            tv_state['notification'] = "Opening Netflix..."
            
    elif button_code == 0x03:  # Amazon Prime
        if tv_state['powered_on']:
            tv_state['current_app'] = "Amazon Prime"
            tv_state['notification'] = "Opening Amazon Prime..."
            
    elif button_code == 0x04:  # HBO Max
        if tv_state['powered_on']:
            tv_state['current_app'] = "HBO Max"
            tv_state['notification'] = "Opening HBO Max..."
            
    elif button_code == 0xA0:  # Game Mode
        if tv_state['powered_on']:
            tv_state['game_mode'] = not tv_state['game_mode']
            tv_state['notification'] = f"Game Mode: {'ON' if tv_state['game_mode'] else 'OFF'}"
            
    elif button_code >= 0x50 and button_code <= 0x59:  # Number pad
        if tv_state['powered_on']:
            digit = button_code - 0x50
            if 'channel_input_time' not in tv_state:
                tv_state['channel_input'] = ""
                tv_state['channel_input_time'] = time.time()
            tv_state['channel_input'] += str(digit)
            tv_state['channel_input_time'] = time.time()
            if len(tv_state['channel_input']) >= 3:
                try:
                    tv_state['channel'] = int(tv_state['channel_input'])
                    tv_state['channel_input'] = ""
                    tv_state['notification'] = f"Channel: {tv_state['channel']}"
                except:
                    tv_state['channel_input'] = ""
    
    # Clear channel input after timeout (in a separate thread)
    if 'channel_input' in tv_state and tv_state['channel_input']:
        if 'channel_input_time' in tv_state:
            if time.time() - tv_state['channel_input_time'] > 2.0:
                tv_state['channel_input'] = ""
                if 'channel_input_time' in tv_state:
                    del tv_state['channel_input_time']
    
    # Broadcast state update to all connected clients
    socketio.emit('tv_state_update', tv_state)
    
    # Clear notification after 2 seconds
    def clear_notification():
        time.sleep(2)
        tv_state['notification'] = None
        socketio.emit('tv_state_update', tv_state)
    
    threading.Thread(target=clear_notification, daemon=True).start()

@app.route('/')
def index():
    """Serve the main 3D TV interface"""
    return render_template('index.html')

@app.route('/api/state')
def get_state():
    """Get current TV state (REST API)"""
    return tv_state

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"[Web Server] Client connected: {request.sid}")
    emit('tv_state_update', tv_state)
    emit('connected', {'message': 'Connected to Virtual TV Simulator'})

@socketio.on('request_state')
def handle_request_state():
    """Handle state request from client"""
    emit('tv_state_update', tv_state)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"[Web Server] Client disconnected: {request.sid}")

@socketio.on('button_press')
def handle_button_press_ws(data):
    """Handle button press from web client via WebSocket"""
    button_code = data.get('button_code')
    if button_code is not None:
        handle_button_press(button_code)

@app.route('/api/button', methods=['POST'])
def api_button_press():
    """Handle button press via REST API"""
    data = request.get_json()
    button_code = data.get('button_code')
    if button_code is not None:
        handle_button_press(button_code)
        return {'status': 'success', 'button_code': button_code}
    return {'status': 'error', 'message': 'Invalid button_code'}, 400

# IPC integration for C program
def start_ipc_listener():
    """Listen for IPC commands from C program"""
    import queue
    from ipc_server import ipc_listener
    
    command_queue = queue.Queue()
    stop_event = threading.Event()
    
    def process_commands():
        """Process commands from IPC queue"""
        while not stop_event.is_set():
            try:
                if not command_queue.empty():
                    button_code = command_queue.get_nowait()
                    handle_button_press(button_code)
            except:
                pass
            time.sleep(0.1)
    
    # Start IPC listener
    ipc_thread = threading.Thread(target=ipc_listener, 
                                   args=(command_queue, stop_event),
                                   daemon=True)
    ipc_thread.start()
    
    # Start command processor
    processor_thread = threading.Thread(target=process_commands, daemon=True)
    processor_thread.start()
    
    return stop_event

def main():
    """Main entry point for Poetry script"""
    print("=" * 60)
    print("  Virtual TV Simulator - Web Server")
    print("=" * 60)
    print()
    print("Starting web server...")
    print("Access the 3D TV interface at: http://localhost:5000")
    print("Press Ctrl+C to stop")
    print()
    
    # Start IPC listener for C program integration
    try:
        stop_event = start_ipc_listener()
        print("[Web Server] IPC listener started (C program integration enabled)")
    except Exception as e:
        print(f"[Web Server] IPC listener failed: {e}")
        print("[Web Server] Web interface will still work, but C program won't connect")
    
    # Run server
    try:
        socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        print("\nShutting down server...")
        if 'stop_event' in locals():
            stop_event.set()

if __name__ == '__main__':
    main()

