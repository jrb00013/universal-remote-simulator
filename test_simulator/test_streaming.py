#!/usr/bin/env python3
"""
Direct Streaming Services Test
Tests all streaming service buttons (YouTube, Netflix, Amazon Prime, HBO Max)
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

# Expected app colors (for verification)
EXPECTED_COLORS = {
    'YouTube': '#FF0000',
    'Netflix': '#E50914',
    'Amazon Prime': '#00A8E1',
    'HBO Max': '#800080'
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

def press_button(button_code, button_name):
    """Press a button and return success status"""
    try:
        response = requests.post(
            API_URL,
            json={'button_code': button_code},
            headers={'Content-Type': 'application/json'},
            timeout=2
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Error pressing {button_name}: {e}")
        return False

def test_streaming_service(service_name, button_code):
    """Test a single streaming service"""
    print(f"\n{'='*60}")
    print(f"Testing: {service_name}")
    print(f"{'='*60}")
    
    # Get initial state
    initial_state = get_tv_state()
    if not initial_state:
        print(f"❌ Failed to get initial state")
        return False
    
    initial_app = initial_state.get('current_app', 'Unknown')
    print(f"Current app: {initial_app}")
    
    # Make sure TV is on
    if not initial_state.get('powered_on', False):
        print("TV is OFF. Turning on...")
        if not press_button(0x10, 'Power'):
            print("❌ Failed to turn on TV")
            return False
        time.sleep(2.5)  # Wait for power-on animation
    
    # Press streaming service button
    print(f"Pressing {service_name} button (0x{button_code:02X})...")
    if not press_button(button_code, service_name):
        print(f"❌ Failed to press {service_name} button")
        return False
    
    # Wait for state update
    time.sleep(0.8)
    
    # Verify state change
    new_state = get_tv_state()
    if not new_state:
        print(f"❌ Failed to get new state")
        return False
    
    new_app = new_state.get('current_app', 'Unknown')
    print(f"New app: {new_app}")
    
    # Verify
    if new_app == service_name:
        print(f"✅ {service_name} opened successfully!")
        print(f"   Expected color: {EXPECTED_COLORS.get(service_name, 'Unknown')}")
        return True
    else:
        print(f"❌ Failed: Expected '{service_name}', got '{new_app}'")
        return False

def test_all_streaming_services():
    """Test all streaming services in sequence"""
    print("\n" + "="*60)
    print("STREAMING SERVICES DIRECT TEST")
    print("="*60)
    print("\nMake sure the web server is running:")
    print("  cd test_simulator")
    print("  poetry run web-server")
    print("\nPress Enter to start testing...")
    input()
    
    # Check server
    if not check_server():
        print("❌ Server is not running!")
        print("Please start it with: poetry run web-server")
        return False
    
    print("✅ Server is running")
    
    # Get initial state
    state = get_tv_state()
    if state:
        print(f"Initial TV state: Power={state.get('powered_on')}, App={state.get('current_app')}")
    
    results = []
    
    # Test each streaming service
    for service_name, button_code in STREAMING_SERVICES.items():
        success = test_streaming_service(service_name, button_code)
        results.append((service_name, success))
        time.sleep(1)  # Brief pause between tests
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for service_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {service_name}")
    
    print(f"\nTotal: {passed}/{total} streaming services working")
    
    if passed == total:
        print("\n🎉 All streaming services are working correctly!")
    else:
        print(f"\n⚠️  {total - passed} streaming service(s) failed")
    
    return passed == total

def test_rapid_switching():
    """Test rapid switching between streaming services"""
    print("\n" + "="*60)
    print("RAPID SWITCHING TEST")
    print("="*60)
    
    if not check_server():
        print("❌ Server is not running!")
        return False
    
    # Make sure TV is on
    state = get_tv_state()
    if state and not state.get('powered_on', False):
        print("Turning TV on...")
        press_button(0x10, 'Power')
        time.sleep(2.5)
    
    print("Rapidly switching between streaming services...")
    
    services = list(STREAMING_SERVICES.items())
    for i in range(3):  # 3 cycles
        print(f"\nCycle {i+1}:")
        for service_name, button_code in services:
            print(f"  → {service_name}", end="", flush=True)
            press_button(button_code, service_name)
            time.sleep(0.5)
            
            # Verify
            state = get_tv_state()
            if state and state.get('current_app') == service_name:
                print(" ✅")
            else:
                print(" ❌")
    
    print("\n✅ Rapid switching test complete")
    return True

def main():
    """Main test function"""
    print("\n" + "="*60)
    print("STREAMING SERVICES DIRECT TEST SUITE")
    print("="*60)
    print("\nThis will test:")
    print("  - YouTube (0x01)")
    print("  - Netflix (0x02)")
    print("  - Amazon Prime (0x03)")
    print("  - HBO Max (0x04)")
    print("\nOptions:")
    print("  1. Test all streaming services")
    print("  2. Test rapid switching")
    print("  3. Test individual service")
    print("  0. Exit")
    
    choice = input("\nEnter choice: ").strip()
    
    if choice == '1':
        test_all_streaming_services()
    elif choice == '2':
        test_rapid_switching()
    elif choice == '3':
        print("\nAvailable services:")
        for i, (name, code) in enumerate(STREAMING_SERVICES.items(), 1):
            print(f"  {i}. {name} (0x{code:02X})")
        service_choice = input("\nEnter service number: ").strip()
        try:
            idx = int(service_choice) - 1
            if 0 <= idx < len(STREAMING_SERVICES):
                service_name = list(STREAMING_SERVICES.keys())[idx]
                button_code = STREAMING_SERVICES[service_name]
                test_streaming_service(service_name, button_code)
            else:
                print("Invalid choice")
        except:
            print("Invalid input")
    elif choice == '0':
        print("Exiting...")
    else:
        print("Invalid choice")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(1)

