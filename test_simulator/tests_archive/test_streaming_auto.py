#!/usr/bin/env python3
"""
Automated Streaming Services Test
Automatically tests all streaming services without user input
"""

import time
import requests
import sys

BASE_URL = "http://localhost:5000"
API_URL = f"{BASE_URL}/api/button"
STATE_URL = f"{BASE_URL}/api/state"

# Streaming service button codes
STREAMING_SERVICES = {
    'YouTube': 0x01,
    'Netflix': 0x02,
    'Amazon Prime': 0x03,
    'HBO Max': 0x04
}

def check_server():
    """Check if server is running"""
    try:
        response = requests.get(STATE_URL, timeout=2)
        return response.status_code == 200
    except:
        return False

def get_tv_state():
    """Get current TV state"""
    try:
        response = requests.get(STATE_URL, timeout=2)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error getting state: {e}")
        return None

def press_button(button_code):
    """Press a button"""
    try:
        response = requests.post(
            API_URL,
            json={'button_code': button_code},
            headers={'Content-Type': 'application/json'},
            timeout=2
        )
        return response.status_code == 200
    except:
        return False

def test_streaming_services():
    """Test all streaming services"""
    print("="*60)
    print("STREAMING SERVICES AUTOMATED TEST")
    print("="*60)
    
    # Check server
    if not check_server():
        print("❌ Server is not running!")
        print("Please start it with: poetry run web-server")
        return False
    
    print("✅ Server is running\n")
    
    # Get initial state
    state = get_tv_state()
    if state:
        print(f"Initial state: Power={state.get('powered_on')}, App={state.get('current_app')}\n")
    
    # Make sure TV is on
    if not state or not state.get('powered_on', False):
        print("Turning TV ON...")
        press_button(0x10)  # Power
        time.sleep(2.5)  # Wait for power-on animation
        print("✅ TV is now ON\n")
    
    results = []
    
    # Test each streaming service
    for service_name, button_code in STREAMING_SERVICES.items():
        print(f"Testing {service_name}...", end=" ", flush=True)
        
        # Press button
        if not press_button(button_code):
            print("❌ FAIL (button press failed)")
            results.append((service_name, False))
            continue
        
        # Wait for state update
        time.sleep(1.0)
        
        # Verify
        new_state = get_tv_state()
        if new_state and new_state.get('current_app') == service_name:
            print(f"✅ PASS - App switched to {service_name}")
            results.append((service_name, True))
        else:
            expected = service_name
            actual = new_state.get('current_app', 'Unknown') if new_state else 'No state'
            print(f"❌ FAIL - Expected '{expected}', got '{actual}'")
            results.append((service_name, False))
        
        time.sleep(0.5)  # Brief pause
    
    # Summary
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for service_name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {service_name}")
    
    print(f"\nTotal: {passed}/{total} passed")
    
    if passed == total:
        print("\n🎉 All streaming services working!")
        return True
    else:
        print(f"\n⚠️  {total - passed} service(s) failed")
        return False

if __name__ == "__main__":
    try:
        success = test_streaming_services()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted.")
        sys.exit(1)

