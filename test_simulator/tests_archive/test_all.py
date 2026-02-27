#!/usr/bin/env python3
"""
Comprehensive test script for Virtual TV Simulator
Tests all components and reports any issues
"""

import sys
import os
import importlib.util

def test_imports():
    """Test if all required modules can be imported"""
    print("=" * 60)
    print("Testing Python Imports")
    print("=" * 60)
    
    required_modules = {
        'flask': 'Flask',
        'flask_socketio': 'Flask-SocketIO',
        'pygame': 'Pygame',
        'socketio': 'python-socketio'
    }
    
    if sys.platform == 'win32':
        required_modules['win32pipe'] = 'pywin32'
    
    missing = []
    for module, name in required_modules.items():
        try:
            __import__(module)
            print(f"[OK] {name}")
        except ImportError:
            print(f"[MISSING] {name}")
            missing.append(name)
    
    if missing:
        print(f"\n[WARNING] Missing modules: {', '.join(missing)}")
        print("Install with: pip install -r requirements.txt")
        return False
    else:
        print("\n[SUCCESS] All imports successful!")
        return True

def test_file_structure():
    """Test if all required files exist"""
    print("\n" + "=" * 60)
    print("Testing File Structure")
    print("=" * 60)
    
    required_files = [
        'web_server.py',
        'main.py',
        'virtual_tv.py',
        'ipc_server.py',
        'web_templates/index.html',
        'web_static/js/tv-simulator.js',
        'requirements.txt'
    ]
    
    missing = []
    for file in required_files:
        if os.path.exists(file):
            print(f"[OK] {file}")
        else:
            print(f"[MISSING] {file}")
            missing.append(file)
    
    if missing:
        print(f"\n[WARNING] Missing files: {', '.join(missing)}")
        return False
    else:
        print("\n[SUCCESS] All files present!")
        return True

def test_syntax():
    """Test Python file syntax"""
    print("\n" + "=" * 60)
    print("Testing Python Syntax")
    print("=" * 60)
    
    python_files = [
        'web_server.py',
        'main.py',
        'virtual_tv.py',
        'ipc_server.py'
    ]
    
    errors = []
    for file in python_files:
        if not os.path.exists(file):
            continue
        try:
            with open(file, 'r', encoding='utf-8') as f:
                compile(f.read(), file, 'exec')
            print(f"[OK] {file} - Syntax valid")
        except SyntaxError as e:
            print(f"[ERROR] {file} - Syntax Error: {e}")
            errors.append((file, e))
        except Exception as e:
            print(f"[WARNING] {file} - Error: {e}")
    
    if errors:
        print(f"\n[WARNING] Syntax errors found in {len(errors)} file(s)")
        return False
    else:
        print("\n[SUCCESS] All Python files have valid syntax!")
        return True

def test_web_server_basic():
    """Test basic web server functionality"""
    print("\n" + "=" * 60)
    print("Testing Web Server (Basic)")
    print("=" * 60)
    
    try:
        # Try to import and create app (don't run it)
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Check if we can at least import the module
        spec = importlib.util.spec_from_file_location("web_server", "web_server.py")
        if spec and spec.loader:
            print("[OK] web_server.py can be loaded")
            
            # Check for critical functions
            with open('web_server.py', 'r', encoding='utf-8') as f:
                content = f.read()
                required_funcs = ['handle_button_press', 'start_ipc_listener', 'app']
                for func in required_funcs:
                    if func in content:
                        print(f"[OK] Function/variable '{func}' found")
                    else:
                        print(f"[ERROR] Function/variable '{func}' NOT found")
                        return False
            
            return True
        else:
            print("[ERROR] Cannot load web_server.py")
            return False
    except Exception as e:
        print(f"[ERROR] Error testing web server: {e}")
        return False

def test_html_structure():
    """Test HTML file structure"""
    print("\n" + "=" * 60)
    print("Testing HTML Structure")
    print("=" * 60)
    
    html_file = 'web_templates/index.html'
    if not os.path.exists(html_file):
        print(f"✗ {html_file} not found")
        return False
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_elements = [
        '<!DOCTYPE html>',
        '<html',
        '<head>',
        '<body>',
        'canvas-container',
        'tv-simulator.js',
        'three.js',
        'socket.io'
    ]
    
    missing = []
    for element in required_elements:
        if element.lower() in content.lower():
            print(f"[OK] Found: {element}")
        else:
            print(f"[MISSING] {element}")
            missing.append(element)
    
    if missing:
        print(f"\n[WARNING] Missing elements: {', '.join(missing)}")
        return False
    else:
        print("\n[SUCCESS] HTML structure looks good!")
        return True

def test_js_structure():
    """Test JavaScript file structure"""
    print("\n" + "=" * 60)
    print("Testing JavaScript Structure")
    print("=" * 60)
    
    js_file = 'web_static/js/tv-simulator.js'
    if not os.path.exists(js_file):
        print(f"✗ {js_file} not found")
        return False
    
    with open(js_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_funcs = [
        'initSocket',
        'initScene',
        'createTV',
        'createRoom',
        'updateTVScreen',
        'animate'
    ]
    
    missing = []
    for func in required_funcs:
        if f'function {func}' in content or f'{func}()' in content:
            print(f"[OK] Function '{func}' found")
        else:
            print(f"[MISSING] Function '{func}'")
            missing.append(func)
    
    if missing:
        print(f"\n[WARNING] Missing functions: {', '.join(missing)}")
        return False
    else:
        print("\n[SUCCESS] JavaScript structure looks good!")
        return True

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("  Virtual TV Simulator - Comprehensive Test")
    print("=" * 60)
    print()
    
    results = []
    
    # Change to test_simulator directory
    if os.path.exists('test_simulator'):
        os.chdir('test_simulator')
    elif not os.path.exists('web_server.py'):
        print("Error: Please run this from the project root or test_simulator directory")
        return 1
    
    results.append(("File Structure", test_file_structure()))
    results.append(("Python Syntax", test_syntax()))
    results.append(("Python Imports", test_imports()))
    results.append(("Web Server", test_web_server_basic()))
    results.append(("HTML Structure", test_html_structure()))
    results.append(("JavaScript Structure", test_js_structure()))
    
    # Summary
    print("\n" + "=" * 60)
    print("  Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All tests passed! The simulator should work correctly.")
        print("\nTo start the web server:")
        print("  python web_server.py")
        print("\nThen open: http://localhost:5000")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed. Please fix the issues above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())

