#!/usr/bin/env python3
"""
Standalone test script for Virtual TV Simulator
Tests the simulator by sending button codes directly
"""

import sys
import time
import queue
import threading
from virtual_tv import VirtualTV
from ipc_server import ipc_listener

def send_test_commands(command_queue):
    """Send a sequence of test commands"""
    test_sequence = [
        (0x10, "Power ON"),
        (0x11, "Volume Up"),
        (0x11, "Volume Up"),
        (0x14, "Channel Up"),
        (0x14, "Channel Up"),
        (0x01, "YouTube"),
        (0x22, "Back"),
        (0x02, "Netflix"),
        (0x22, "Back"),
        (0x21, "Menu"),
        (0x22, "Back"),
        (0x70, "Info"),
        (0x22, "Back"),
        (0x13, "Mute"),
        (0x13, "Mute"),
        (0x12, "Volume Down"),
        (0x51, "Channel 1"),
        (0x52, "Channel 2"),
        (0x53, "Channel 3"),
        (0xA0, "Game Mode"),
        (0x10, "Power OFF"),
    ]
    
    print("\n" + "="*60)
    print("  Test Sequence Starting")
    print("="*60)
    print("The simulator will receive commands automatically.")
    print("Watch the TV respond to each button press!\n")
    
    for button_code, description in test_sequence:
        print(f"[TEST] Sending: {description} (0x{button_code:02X})")
        command_queue.put(button_code)
        time.sleep(1.5)  # Wait between commands
    
    print("\n" + "="*60)
    print("  Test Sequence Complete")
    print("="*60)
    print("The simulator will continue running. Press ESC to exit.\n")

def main():
    print("=" * 60)
    print("  Virtual TV Simulator - Standalone Test")
    print("=" * 60)
    print()
    print("This will run a test sequence automatically.")
    print("The simulator will respond to all commands.")
    print()
    
    # Check for pygame
    try:
        import pygame
    except ImportError:
        print("ERROR: pygame is not installed!")
        print("Please install it with: pip install pygame")
        sys.exit(1)
    
    # Create command queue
    command_queue = queue.Queue()
    stop_event = threading.Event()
    
    # Start test command sender in a separate thread
    test_thread = threading.Thread(target=send_test_commands, 
                                   args=(command_queue,),
                                   daemon=True)
    test_thread.start()
    
    # Create and run TV
    tv = VirtualTV()
    try:
        tv.run(command_queue)
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        stop_event.set()
        print("Test complete.")

if __name__ == "__main__":
    main()

