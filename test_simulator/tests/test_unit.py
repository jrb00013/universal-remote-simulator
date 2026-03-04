"""
Unit tests for Virtual TV Simulator
Tests individual components and functions.
All file paths use SIMULATOR_ROOT so tests run from repo root or test_simulator.
"""
import pytest
import sys
import os

# Add parent directory to path
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
SIMULATOR_ROOT = os.path.dirname(TESTS_DIR)
sys.path.insert(0, SIMULATOR_ROOT)


def _path(*parts):
    """Path relative to test_simulator root."""
    return os.path.join(SIMULATOR_ROOT, *parts)


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
    """Test that all required files exist (paths relative to test_simulator root)."""
    
    def test_web_server_exists(self):
        """Test web_server.py exists"""
        assert os.path.isfile(_path('web_server.py'))
    
    def test_main_exists(self):
        """Test main.py exists"""
        assert os.path.isfile(_path('main.py'))
    
    def test_virtual_tv_exists(self):
        """Test virtual_tv.py exists"""
        assert os.path.isfile(_path('virtual_tv.py'))
    
    def test_ipc_server_exists(self):
        """Test ipc_server.py exists"""
        assert os.path.isfile(_path('ipc_server.py'))
    
    def test_html_template_exists(self):
        """Test HTML template exists"""
        assert os.path.isfile(_path('web_templates', 'index.html'))
    
    def test_js_file_exists(self):
        """Test simulator JavaScript modules exist"""
        base = _path('web_static', 'js', 'simulator')
        assert os.path.isdir(base), "simulator/ directory missing"
        assert os.path.isfile(os.path.join(base, 'main.js')), "simulator/main.js missing"
        assert os.path.isfile(os.path.join(base, 'globals.js')), "simulator/globals.js missing"
    
    def test_requirements_exists(self):
        """Test requirements.txt exists"""
        assert os.path.isfile(_path('requirements.txt'))
    
    def test_button_codes_exists(self):
        """Test button_codes.py exists (single source of truth for codes)."""
        assert os.path.isfile(_path('button_codes.py'))

    def test_brand_detection_exists(self):
        """Test brand_detection.py exists (keyword-based brand detection)."""
        assert os.path.isfile(_path('brand_detection.py'))

    def test_scheduler_exists(self):
        """Test scheduler.py exists (autonomous time rules + presets)."""
        assert os.path.isfile(_path('scheduler.py'))

    def test_autonomous_config_exists(self):
        """Test autonomous_config.json exists for scheduler."""
        assert os.path.isfile(_path('autonomous_config.json'))

    def test_ir_synthetic_exists(self):
        """Test ir_synthetic.py exists (synthetic NEC/RC5/RC6 pulse-length generator)."""
        assert os.path.isfile(_path('ir_synthetic.py'))

    def test_protocol_classifier_exists(self):
        """Test protocol_classifier.py exists (IR protocol classifier)."""
        assert os.path.isfile(_path('protocol_classifier.py'))

    def test_brand_detection_test_file_exists(self):
        """Test test_brand_detection.py exists (ML audit: brand detection)."""
        assert os.path.isfile(_path('tests', 'test_brand_detection.py'))

    def test_protocol_classifier_test_file_exists(self):
        """Test test_protocol_classifier.py exists (ML audit: protocol classifier)."""
        assert os.path.isfile(_path('tests', 'test_protocol_classifier.py'))

    def test_ir_synthetic_test_file_exists(self):
        """Test test_ir_synthetic.py exists (ML audit: synthetic IR data)."""
        assert os.path.isfile(_path('tests', 'test_ir_synthetic.py'))


class TestSyntax:
    """Test Python file syntax (paths relative to test_simulator root)."""
    
    @pytest.mark.parametrize('relpath', [
        'web_server.py', 'main.py', 'virtual_tv.py', 'ipc_server.py', 'button_codes.py',
        'brand_detection.py', 'scheduler.py', 'ir_synthetic.py', 'protocol_classifier.py',
    ])
    def test_python_syntax(self, relpath):
        """Test Python file compiles without syntax errors."""
        path = _path(relpath)
        if not os.path.exists(path):
            pytest.skip(f"File not found: {relpath}")
        with open(path, 'r', encoding='utf-8') as f:
            compile(f.read(), path, 'exec')


class TestHTMLStructure:
    """Test HTML file structure (paths relative to test_simulator root)."""
    
    def test_html_doctype(self):
        """Test HTML has DOCTYPE"""
        path = _path('web_templates', 'index.html')
        if not os.path.exists(path):
            pytest.skip("index.html not found")
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert '<!DOCTYPE html>' in content
    
    def test_html_structure(self):
        """Test HTML has required elements"""
        path = _path('web_templates', 'index.html')
        if not os.path.exists(path):
            pytest.skip("index.html not found")
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read().lower()
            assert '<html' in content
            assert '<head>' in content
            assert '<body>' in content
    
    def test_html_canvas(self):
        """Test HTML has canvas container"""
        path = _path('web_templates', 'index.html')
        if not os.path.exists(path):
            pytest.skip("index.html not found")
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'canvas-container' in content or 'canvas' in content
    
    def test_html_scripts(self):
        """Test HTML includes required scripts (modular simulator or legacy tv-simulator.js)"""
        path = _path('web_templates', 'index.html')
        if not os.path.exists(path):
            pytest.skip("index.html not found")
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read().lower()
        has_simulator = 'simulator/' in content and 'simulator/main.js' in content
        has_legacy = 'tv-simulator.js' in content
        assert has_simulator or has_legacy, "index.html must load simulator/main.js or tv-simulator.js"
        assert 'three.js' in content or 'three' in content
        assert 'socket.io' in content


class TestJavaScriptStructure:
    """Test JavaScript file structure (paths relative to test_simulator root)."""
    
    def test_js_file_readable(self):
        """Test simulator main.js is readable"""
        path = _path('web_static', 'js', 'simulator', 'main.js')
        if not os.path.exists(path):
            pytest.skip("simulator/main.js not found")
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert len(content) > 0

    def test_js_has_functions(self):
        """Test simulator has required functions across modules"""
        base = _path('web_static', 'js', 'simulator')
        if not os.path.isdir(base):
            pytest.skip("simulator/ not found")
        content = ""
        for name in ['main.js', 'scene.js', 'socket-state.js', 'screen.js']:
            p = os.path.join(base, name)
            if os.path.isfile(p):
                with open(p, 'r', encoding='utf-8') as f:
                    content += f.read()
        assert 'function' in content or '=>' in content or 'const' in content

    def test_js_has_socket(self):
        """Test simulator has socket initialization"""
        path = _path('web_static', 'js', 'simulator', 'socket-state.js')
        if not os.path.exists(path):
            pytest.skip("simulator/socket-state.js not found")
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'socket' in content.lower() or 'io(' in content.lower()

