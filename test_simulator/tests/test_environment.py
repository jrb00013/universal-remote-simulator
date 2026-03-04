"""
Environment and structure tests: imports, file layout, syntax, HTML/JS structure.
No server required. Integrates checks from the former tests_archive test_all.py.
"""
import os
import sys
import pytest

# Simulator root = parent of tests/
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
SIMULATOR_ROOT = os.path.dirname(TESTS_DIR)


def _path(*parts):
    return os.path.join(SIMULATOR_ROOT, *parts)


class TestFileStructure:
    """Required files and directories exist."""

    def test_web_server_exists(self):
        assert os.path.isfile(_path("web_server.py"))

    def test_main_exists(self):
        assert os.path.isfile(_path("main.py"))

    def test_virtual_tv_exists(self):
        assert os.path.isfile(_path("virtual_tv.py"))

    def test_ipc_server_exists(self):
        assert os.path.isfile(_path("ipc_server.py"))

    def test_index_html_exists(self):
        assert os.path.isfile(_path("web_templates", "index.html"))

    def test_tv_simulator_js_exists(self):
        # Modular simulator: simulator/main.js and globals.js
        base = _path("web_static", "js", "simulator")
        assert os.path.isdir(base), "simulator/ directory missing"
        assert os.path.isfile(os.path.join(base, "main.js")), "simulator/main.js missing"


class TestPythonSyntax:
    """Python files compile without syntax errors."""

    @pytest.mark.parametrize("relpath", ["web_server.py", "main.py", "virtual_tv.py", "ipc_server.py"])
    def test_syntax(self, relpath):
        path = _path(relpath)
        if not os.path.exists(path):
            pytest.skip(f"File not found: {relpath}")
        with open(path, "r", encoding="utf-8") as f:
            compile(f.read(), path, "exec")


class TestImports:
    """Required Python modules can be imported."""

    def test_flask_import(self):
        import flask  # noqa: F401

    def test_flask_socketio_import(self):
        import flask_socketio  # noqa: F401

    def test_socketio_client_import(self):
        import socketio  # noqa: F401

    @pytest.mark.parametrize("module", ["pygame"])
    def test_optional_imports(self, module):
        try:
            __import__(module)
        except ImportError:
            pytest.skip(f"{module} not installed")


class TestWebServerModule:
    """Web server module has expected symbols."""

    def test_web_server_loadable(self):
        path = _path("web_server.py")
        if not os.path.isfile(path):
            pytest.skip("web_server.py not found")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        for name in ["handle_button_press", "start_ipc_listener", "app"]:
            assert name in content, f"Expected '{name}' in web_server.py"


class TestHTMLStructure:
    """index.html contains required elements and script references."""

    def test_html_has_required_elements(self):
        path = _path("web_templates", "index.html")
        if not os.path.isfile(path):
            pytest.skip("index.html not found")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().lower()
        required = [
            "<!doctype html>",
            "<html",
            "<head>",
            "<body>",
            "canvas-container",
            "simulator/",
            "three.js",
            "socket.io",
        ]
        for element in required:
            assert element in content, f"Missing in index.html: {element}"


class TestJSStructure:
    """Simulator modules contain expected function names."""

    def test_js_has_expected_functions(self):
        base = _path("web_static", "js", "simulator")
        if not os.path.isdir(base):
            pytest.skip("simulator/ not found")
        content = ""
        for name in os.listdir(base):
            if name.endswith(".js"):
                with open(os.path.join(base, name), "r", encoding="utf-8") as f:
                    content += f.read()
        required = [
            "initSocket",
            "initScene",
            "createTV",
            "createRoom",
            "updateTVScreen",
            "animate",
        ]
        for fn in required:
            assert (
                f"function {fn}" in content or f"{fn}()" in content or f"{fn} (" in content
            ), f"Expected '{fn}' in simulator modules"
