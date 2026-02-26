#!/usr/bin/env python3
"""
Simple Streaming Services Test
Quick test of all streaming service buttons
"""

import time
import requests

BASE_URL = "http://localhost:5000"
API_URL = f"{BASE_URL}/api/button"
STATE_URL = f"{BASE_URL}/api/state"

STREAMING_SERVICES = {
    'YouTube': 0x01,
    'Netflix': 0x02,
    'Amazon Prime': 0x03,
    'HBO Max': 0x04
}

def press_button(button_code):
    """Press a button"""
    try:
        requests.post(API_URL, json={'button_code': button_code}, timeout=1)
        return True
    except:
        return False

def get_state():
    """Get TV state"""
    try:
        response = requests.get(STATE_URL, timeout=1)
        return response.json() if response.status_code == 200 else None
    except:
        return None

def main():
    print("="*60)
    print("STREAMING SERVICES TEST")
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
        press_button(0x10)
        time.sleep(2.5)
    
    print("Testing streaming services:\n")
    
    # Test each service
    for service_name, button_code in STREAMING_SERVICES.items():
        print(f"-> {service_name}...", end=" ", flush=True)
        press_button(button_code)
        time.sleep(1.2)  # Wait for animation
        
        state = get_state()
        if state and state.get('current_app') == service_name:
            print("[PASS]")
        else:
            print("[FAIL]")
        
        time.sleep(0.5)
    
    print("\n[OK] Test complete! Check the browser to see the animations.")
    print("   You should see:")
    print("   - YouTube: Red screen")
    print("   - Netflix: Dark red screen")
    print("   - Amazon Prime: Blue screen")
    print("   - HBO Max: Purple screen")

if __name__ == "__main__":
    main()

