# WSL/Linux Setup Guide

## ⚠️ Important: Use Poetry, Not pip!

Modern Linux distributions (Ubuntu 23.04+, Debian 12+) block direct `pip install` to protect system Python. You'll see this error:

```
error: externally-managed-environment
× This environment is externally managed
```

**Solution: Use Poetry!** Poetry automatically creates isolated virtual environments.

## Quick Setup for WSL

### 1. Install Poetry

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### 2. Add Poetry to PATH

Add to your `~/.bashrc` or `~/.zshrc`:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

Then reload:
```bash
source ~/.bashrc
# or
source ~/.zshrc
```

### 3. Verify Poetry Installation

```bash
poetry --version
```

Should show something like: `Poetry (version 1.7.0)`

### 4. Install Dependencies

```bash
cd test_simulator
poetry install
```

Poetry will:
- Create a virtual environment automatically
- Install all dependencies (Flask, SocketIO, Pygame, etc.)
- Handle platform-specific packages
- Create a `poetry.lock` file for reproducible builds

### 5. Run the Simulator

**Web Server (3D/VR):**
```bash
poetry run web-server
```

**Desktop Simulator:**
```bash
poetry run desktop-simulator
```

## Using Poetry Shell (Optional)

Activate Poetry's virtual environment to run commands directly:

```bash
poetry shell
# Now you're in the virtual environment
python web_server.py
python main.py
# Exit with: exit
```

## Troubleshooting

### Poetry command not found
```bash
# Check if Poetry is installed
ls ~/.local/bin/poetry

# If not, reinstall and add to PATH
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"
```

### Permission errors
```bash
# Make sure Poetry is executable
chmod +x ~/.local/bin/poetry
```

### Virtual environment issues
```bash
# Remove and recreate
poetry env remove python
poetry install
```

### Still getting pip errors?
**Don't use pip!** Always use Poetry:
- ❌ `pip install flask` → ✅ `poetry add flask`
- ❌ `pip install -r requirements.txt` → ✅ `poetry install`
- ❌ `python -m pip install ...` → ✅ `poetry install`

## Why Poetry?

1. **Isolated Environments**: Each project has its own virtual environment
2. **No System Conflicts**: Doesn't touch system Python
3. **Dependency Locking**: `poetry.lock` ensures reproducible builds
4. **Cross-platform**: Works the same on Windows, Linux, Mac
5. **Modern Standard**: Recommended by Python Packaging Authority

## Alternative: Manual Virtual Environment

If you really can't use Poetry (not recommended):

```bash
python3 -m venv venv
source venv/bin/activate
pip install flask flask-socketio python-socketio pygame
python web_server.py
```

But Poetry is much better! Use Poetry instead.

## Next Steps

Once Poetry is set up:
1. `cd test_simulator`
2. `poetry install`
3. `poetry run web-server`
4. Open http://localhost:5000

That's it! Poetry handles everything.

