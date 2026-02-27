#!/usr/bin/env python3
"""
Comprehensive test script for the Interactive 3D TV Simulator
Tests all features including remote control, IR signals, and button interactions
"""

import time
import requests
import socketio
import sys

BASE_URL = "http://localhost:5000"
API_URL = f"{BASE_URL}/api/button"
STATE_URL = f"{BASE_URL}/api/state"

# Button codes for testing
BUTTON_CODES = {
    'Power': 0x10,
    'Volume Up': 0x11,
    'Volume Down': 0x12,
    'Mute': 0x13,
    'Channel Up': 0x14,
    'Channel Down': 0x15,
    'Home': 0x20,
    'Menu': 0x21,
    'Back': 0x22,
    'YouTube': 0x01,
    'Netflix': 0x02,
    'Amazon Prime': 0x03,
    'HBO Max': 0x04,
    'Game Mode': 0xA0,
    '1': 0x51,
    '2': 0x52,
    '3': 0x53,
}

def test_server_connection():
    """Test if server is running"""
    print("=" * 60)
    print("Testing Server Connection")
    print("=" * 60)
    try:
        response = requests.get(STATE_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and responding")
            state = response.json()
            print(f"   Current TV State: Power={state.get('powered_on')}, Volume={state.get('volume')}%")
            return True
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running?")
        print("   Start with: poetry run web-server")
        return False
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        return False

def test_rest_api():
    """Test REST API button presses"""
    print("\n" + "=" * 60)
    print("Testing REST API")
    print("=" * 60)
    
    tests = [
        ('Power', 0x10),
        ('Volume Up', 0x11),
        ('Volume Up', 0x11),
        ('Channel Up', 0x14),
        ('Home', 0x20),
    ]
    
    passed = 0
    failed = 0
    
    for button_name, button_code in tests:
        try:
            response = requests.post(
                API_URL,
                json={'button_code': button_code},
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    print(f"✅ {button_name} (0x{button_code:02X}) - Success")
                    passed += 1
                else:
                    print(f"❌ {button_name} (0x{button_code:02X}) - Failed: {data}")
                    failed += 1
            else:
                print(f"❌ {button_name} (0x{button_code:02X}) - HTTP {response.status_code}")
                failed += 1
                
            time.sleep(0.5)  # Small delay between requests
            
        except Exception as e:
            print(f"❌ {button_name} (0x{button_code:02X}) - Error: {e}")
            failed += 1
    
    print(f"\nREST API Results: {passed} passed, {failed} failed")
    return failed == 0

def test_websocket():
    """Test WebSocket connection and button presses"""
    print("\n" + "=" * 60)
    print("Testing WebSocket Connection")
    print("=" * 60)
    
    try:
        sio = socketio.Client()
        connected = False
        state_received = False
        
        @sio.on('connect')
        def on_connect():
            nonlocal connected
            connected = True
            print("✅ WebSocket connected")
            sio.emit('request_state')
        
        @sio.on('tv_state_update')
        def on_state_update(data):
            nonlocal state_received
            state_received = True
            print(f"✅ Received state update: Power={data.get('powered_on')}, Volume={data.get('volume')}%")
        
        @sio.on('connected')
        def on_connected(data):
            print(f"✅ Server message: {data.get('message', 'Connected')}")
        
        sio.connect(BASE_URL, wait_timeout=5)
        time.sleep(1)  # Wait for connection
        
        if not connected:
            print("❌ WebSocket connection failed")
            return False
        
        # Test button presses via WebSocket
        print("\nTesting WebSocket button presses...")
        tests = [
            ('Power', 0x10),
            ('Volume Up', 0x11),
            ('Channel Up', 0x14),
        ]
        
        for button_name, button_code in tests:
            sio.emit('button_press', {'button_code': button_code})
            print(f"✅ Sent {button_name} (0x{button_code:02X}) via WebSocket")
            time.sleep(0.5)
        
        time.sleep(1)  # Wait for state updates
        sio.disconnect()
        
        print("✅ WebSocket tests completed")
        return True
        
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        return False

def test_state_consistency():
    """Test that state is consistent across requests"""
    print("\n" + "=" * 60)
    print("Testing State Consistency")
    print("=" * 60)
    
    try:
        # Get initial state
        response1 = requests.get(STATE_URL, timeout=5)
        state1 = response1.json()
        
        # Press a button
        requests.post(API_URL, json={'button_code': 0x11}, timeout=5)  # Volume Up
        time.sleep(0.5)
        
        # Get state again
        response2 = requests.get(STATE_URL, timeout=5)
        state2 = response2.json()
        
        # Check if volume increased
        vol1 = state1.get('volume', 0)
        vol2 = state2.get('volume', 0)
        
        if vol2 > vol1:
            print(f"✅ State updated correctly: Volume {vol1}% -> {vol2}%")
            return True
        else:
            print(f"❌ State not updated: Volume {vol1}% -> {vol2}%")
            return False
            
    except Exception as e:
        print(f"❌ State consistency test failed: {e}")
        return False

def test_all_buttons():
    """Test all available buttons"""
    print("\n" + "=" * 60)
    print("Testing All Button Codes")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for button_name, button_code in BUTTON_CODES.items():
        try:
            response = requests.post(
                API_URL,
                json={'button_code': button_code},
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"✅ {button_name:20s} (0x{button_code:02X})")
                passed += 1
            else:
                print(f"❌ {button_name:20s} (0x{button_code:02X}) - HTTP {response.status_code}")
                failed += 1
                
            time.sleep(0.3)
            
        except Exception as e:
            print(f"❌ {button_name:20s} (0x{button_code:02X}) - Error: {e}")
            failed += 1
    
    print(f"\nButton Tests: {passed} passed, {failed} failed")
    return failed == 0

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("Interactive 3D TV Simulator - Comprehensive Test Suite")
    print("=" * 60)
    print("\nMake sure the web server is running:")
    print("  cd test_simulator")
    print("  poetry run web-server")
    print("\nPress Enter to start tests...")
    input()
    
    results = []
    
    # Test 1: Server connection
    results.append(("Server Connection", test_server_connection()))
    
    if not results[-1][1]:
        print("\n❌ Server is not running. Please start it and try again.")
        return
    
    # Test 2: REST API
    results.append(("REST API", test_rest_api()))
    
    # Test 3: WebSocket
    results.append(("WebSocket", test_websocket()))
    
    # Test 4: State consistency
    results.append(("State Consistency", test_state_consistency()))
    
    # Test 5: All buttons
    results.append(("All Buttons", test_all_buttons()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    total_passed = sum(1 for _, result in results if result)
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 All tests passed! The simulator is fully functional.")
    else:
        print("\n⚠️  Some tests failed. Please check the output above.")
    
    return total_passed == total_tests

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
        sys.exit(1)

