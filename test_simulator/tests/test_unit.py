"""
Unit tests for Virtual TV Simulator
Tests individual components and functions
"""
import pytest
import sys
import os
import importlib.util

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestImports:
    """Test that all required modules can be imported"""
    
    def test_flask_import(self):
        """Test Flask import"""
        import flask
        assert flask is not None
    
    def test_flask_socketio_import(self):
        """Test Flask-SocketIO import"""
        import flask_socketio
        assert flask_socketio is not None
    
    def test_pygame_import(self):
        """Test Pygame import"""
        import pygame
        assert pygame is not None
    
    def test_socketio_import(self):
        """Test python-socketio import"""
        import socketio
        assert socketio is not None
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows only")
    def test_pywin32_import(self):
        """Test pywin32 import (Windows only)"""
        import win32pipe
        assert win32pipe is not None


class TestFileStructure:
    """Test that all required files exist"""
    
    def test_web_server_exists(self):
        """Test web_server.py exists"""
        assert os.path.exists('web_server.py')
    
    def test_main_exists(self):
        """Test main.py exists"""
        assert os.path.exists('main.py')
    
    def test_virtual_tv_exists(self):
        """Test virtual_tv.py exists"""
        assert os.path.exists('virtual_tv.py')
    
    def test_ipc_server_exists(self):
        """Test ipc_server.py exists"""
        assert os.path.exists('ipc_server.py')
    
    def test_html_template_exists(self):
        """Test HTML template exists"""
        assert os.path.exists('web_templates/index.html')
    
    def test_js_file_exists(self):
        """Test JavaScript file exists"""
        assert os.path.exists('web_static/js/tv-simulator.js')
    
    def test_requirements_exists(self):
        """Test requirements.txt exists"""
        assert os.path.exists('requirements.txt')


class TestSyntax:
    """Test Python file syntax"""
    
    def test_web_server_syntax(self):
        """Test web_server.py syntax"""
        with open('web_server.py', 'r', encoding='utf-8') as f:
            compile(f.read(), 'web_server.py', 'exec')
    
    def test_main_syntax(self):
        """Test main.py syntax"""
        with open('main.py', 'r', encoding='utf-8') as f:
            compile(f.read(), 'main.py', 'exec')
    
    def test_virtual_tv_syntax(self):
        """Test virtual_tv.py syntax"""
        with open('virtual_tv.py', 'r', encoding='utf-8') as f:
            compile(f.read(), 'virtual_tv.py', 'exec')
    
    def test_ipc_server_syntax(self):
        """Test ipc_server.py syntax"""
        with open('ipc_server.py', 'r', encoding='utf-8') as f:
            compile(f.read(), 'ipc_server.py', 'exec')


class TestHTMLStructure:
    """Test HTML file structure"""
    
    def test_html_doctype(self):
        """Test HTML has DOCTYPE"""
        with open('web_templates/index.html', 'r', encoding='utf-8') as f:
            content = f.read()
            assert '<!DOCTYPE html>' in content
    
    def test_html_structure(self):
        """Test HTML has required elements"""
        with open('web_templates/index.html', 'r', encoding='utf-8') as f:
            content = f.read().lower()
            assert '<html' in content
            assert '<head>' in content
            assert '<body>' in content
    
    def test_html_canvas(self):
        """Test HTML has canvas container"""
        with open('web_templates/index.html', 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'canvas-container' in content or 'canvas' in content
    
    def test_html_scripts(self):
        """Test HTML includes required scripts"""
        with open('web_templates/index.html', 'r', encoding='utf-8') as f:
            content = f.read().lower()
            assert 'tv-simulator.js' in content
            assert 'three.js' in content or 'three' in content
            assert 'socket.io' in content


class TestJavaScriptStructure:
    """Test JavaScript file structure"""
    
    def test_js_file_readable(self):
        """Test JavaScript file is readable"""
        with open('web_static/js/tv-simulator.js', 'r', encoding='utf-8') as f:
            content = f.read()
            assert len(content) > 0
    
    def test_js_has_functions(self):
        """Test JavaScript has required functions"""
        with open('web_static/js/tv-simulator.js', 'r', encoding='utf-8') as f:
            content = f.read()
            # Check for common function patterns
            assert 'function' in content or '=>' in content or 'const' in content
    
    def test_js_has_socket(self):
        """Test JavaScript has socket initialization"""
        with open('web_static/js/tv-simulator.js', 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'socket' in content.lower() or 'io(' in content.lower()

