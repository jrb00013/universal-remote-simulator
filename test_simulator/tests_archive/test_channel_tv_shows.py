#!/usr/bin/env python3
"""
Test Channel Changes and TV Shows
Verifies that number buttons change channels and show TV content
"""

import time
import requests

BASE_URL = "http://localhost:5000"
API_URL = f"{BASE_URL}/api/button"
STATE_URL = f"{BASE_URL}/api/state"
FRAME_URL = f"{BASE_URL}/api/frame"

# Number button codes (0-9)
NUMBER_BUTTONS = {
    '0': 0x50, '1': 0x51, '2': 0x52, '3': 0x53, '4': 0x54,
    '5': 0x55, '6': 0x56, '7': 0x57, '8': 0x58, '9': 0x59
}

def press_button(button_code):
    """Press a button"""
    try:
        requests.post(API_URL, json={'button_code': button_code}, timeout=1)
        return True
    except Exception as e:
        print(f"Error pressing button: {e}")
        return False

def get_state():
    """Get TV state"""
    try:
        response = requests.get(STATE_URL, timeout=1)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Error getting state: {e}")
        return None

def get_frame_info():
    """Get frame info from streaming API"""
    try:
        response = requests.get(f"{FRAME_URL}/info", timeout=1)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Error getting frame info: {e}")
        return None

def test_channel_change(channel_number):
    """Test changing to a specific channel"""
    print(f"\n-> Testing channel {channel_number}...")
    
    # Press number buttons to enter channel
    channel_str = str(channel_number).zfill(3)  # Pad to 3 digits
    for digit in channel_str:
        button_code = NUMBER_BUTTONS[digit]
        press_button(button_code)
        time.sleep(0.2)  # Small delay between digits
    
    # Wait for channel change to complete
    time.sleep(1.0)
    
    # Check state
    state = get_state()
    if state:
        actual_channel = state.get('channel')
        current_app = state.get('current_app')
        
        print(f"   Channel: {actual_channel} (expected: {channel_number})")
        print(f"   Current App: {current_app} (should be None for TV shows)")
        
        if actual_channel == channel_number:
            if current_app is None:
                print(f"   ✅ Channel {channel_number} set correctly, TV show should be displaying")
                return True
            else:
                print(f"   ⚠️  Channel set but current_app is '{current_app}' (should be None)")
                return False
        else:
            print(f"   ❌ Channel mismatch!")
            return False
    else:
        print("   ❌ Could not get state")
        return False

def main():
    print("="*60)
    print("CHANNEL & TV SHOW TEST")
    print("="*60)
    print("\nMake sure web server is running: poetry run web-server")
    print("Open browser: http://localhost:5000")
    print("\nStarting test in 3 seconds...")
    time.sleep(3)
    
    # Check server
    state = get_state()
    if not state:
        print("[FAIL] Server not running!")
        return
    
    print("[OK] Server connected\n")
    
    # Turn TV on if needed
    if not state.get('powered_on'):
        print("Turning TV ON...")
        press_button(0x10)  # Power button
        time.sleep(2.5)
        state = get_state()
        if not state or not state.get('powered_on'):
            print("[FAIL] Could not turn TV on")
            return
    
    # Test streaming API
    print("\n--- Testing Streaming API ---")
    frame_info = get_frame_info()
    if frame_info:
        print(f"✅ Streaming API working: {frame_info.get('width')}x{frame_info.get('height')}")
    else:
        print("⚠️  Streaming API not responding (may need time to capture first frame)")
    
    # Test channel changes
    print("\n--- Testing Channel Changes ---")
    print("Testing that number buttons change channels and show TV content...")
    
    test_channels = [456, 789, 123, 42, 7]
    passed = 0
    failed = 0
    
    for channel in test_channels:
        if test_channel_change(channel):
            passed += 1
        else:
            failed += 1
        time.sleep(0.5)
    
    # Test that Home button returns to Home screen
    print("\n--- Testing Home Button ---")
    print("-> Pressing Home button...")
    press_button(0x20)  # Home button
    time.sleep(1.0)
    state = get_state()
    if state and state.get('current_app') == 'Home':
        print("   ✅ Home button works correctly")
        passed += 1
    else:
        print(f"   ❌ Home button failed (current_app: {state.get('current_app') if state else 'None'})")
        failed += 1
    
    # Summary
    print("\n" + "="*60)
    print(f"TEST SUMMARY: {passed} passed, {failed} failed")
    print("="*60)
    
    if failed == 0:
        print("\n✅ All tests passed! TV shows should be displaying when you change channels.")
        print("   Check the browser - you should see different TV show content for each channel.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Check the browser to see what's happening.")
    
    print("\nTo test manually:")
    print("  1. Click number buttons on the 3D remote (e.g., 4, 5, 6)")
    print("  2. The TV should switch to that channel and show TV content")
    print("  3. Click Home button to return to Home screen")

if __name__ == "__main__":
    main()

