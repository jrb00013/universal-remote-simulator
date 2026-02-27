# Setup Guide

Complete setup instructions for the Virtual TV Simulator.

## Quick Start

### Install Poetry (if not installed)

**WSL/Linux/Mac:**
```bash
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"
```

**Windows:**
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

### Install Dependencies

```bash
cd test_simulator
poetry install
```

**Note:** Poetry automatically creates a virtual environment and handles all dependencies, including platform-specific ones (like pywin32 on Windows). No pip needed!

### Start the Simulator

**Web Server (3D/VR):**
```bash
poetry run web-server
```
Then open: **http://localhost:5000**

**Desktop Simulator (2D):**
```bash
poetry run desktop-simulator
```

## WSL/Linux Setup

### Important: Use Poetry, Not pip!

Modern Linux distributions (Ubuntu 23.04+, Debian 12+) block direct `pip install` to protect system Python. You'll see this error:

```
error: externally-managed-environment
× This environment is externally managed
```

**Solution: Use Poetry!** Poetry automatically creates isolated virtual environments.

### Setup Steps

1. **Install Poetry:**
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Add Poetry to PATH:**
   Add to your `~/.bashrc` or `~/.zshrc`:
   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```
   Then reload:
   ```bash
   source ~/.bashrc
   ```

3. **Verify Installation:**
   ```bash
   poetry --version
   ```

4. **Install Dependencies:**
   ```bash
   cd test_simulator
   poetry install
   ```

5. **Run the Simulator:**
   ```bash
   poetry run web-server        # Web 3D/VR simulator
   poetry run desktop-simulator  # Desktop 2D simulator
   ```

### Using Poetry Shell (Optional)

Activate Poetry's virtual environment to run commands directly:

```bash
poetry shell
# Now you're in the virtual environment
python web_server.py
python main.py
# Exit with: exit
```

### Troubleshooting

**Poetry command not found:**
```bash
# Check if Poetry is installed
ls ~/.local/bin/poetry

# If not, reinstall and add to PATH
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"
```

**Permission errors:**
```bash
# Make sure Poetry is executable
chmod +x ~/.local/bin/poetry
```

**Virtual environment issues:**
```bash
# Remove and recreate
poetry env remove python
poetry install
```

**Still getting pip errors?**
**Don't use pip!** Always use Poetry:
- ❌ `pip install flask` → ✅ `poetry add flask`
- ❌ `pip install -r requirements.txt` → ✅ `poetry install`

## Alternative: Using pip (Not Recommended)

If you really can't use Poetry:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

On Windows, you may also need:
```bash
pip install pywin32
```

But Poetry is much better! Use Poetry instead.

## Build Remote Control with Simulator Support

In the project root directory:

**For Web Server:**
```bash
make clean
make SIMULATOR=1 WEB=1
```

**For Desktop Simulator:**
```bash
make clean
make SIMULATOR=1
```

## Run the Remote Control

**Windows:**
```bash
bin\remote_control.exe
```

**Unix/Linux/Mac:**
```bash
./bin/remote_control
```

## Server Management

### Check if Server is Running

**Windows PowerShell:**
```powershell
Get-NetTCPConnection -LocalPort 5000
```

**Linux/Mac:**
```bash
netstat -an | grep 5000
# or
lsof -i :5000
```

### Stop the Server

Press `Ctrl+C` in the terminal where the server is running.

### Restart the Server

```bash
cd test_simulator
poetry run web-server
```

## Troubleshooting

### Simulator doesn't receive commands
- Make sure the simulator is running before starting the remote control program
- Check that the remote control was built with `SIMULATOR=1` (and `WEB=1` for web server)
- On Windows, ensure you have administrator privileges if needed for named pipes

### Import errors
- Use Poetry: `poetry install` (handles everything automatically)
- If you see "externally-managed-environment" error, Poetry is the solution!

### Connection errors
- Close and restart both programs
- On Unix, check that `/tmp/phillips_remote_tv.sock` doesn't exist from a previous run
- Make sure only one simulator instance is running

### Server won't start
- Check if port 5000 is already in use
- Install dependencies with Poetry: `poetry install`
- Check Python version (3.7+ required)

### Browser shows blank screen
- Check browser console for errors (F12)
- Ensure WebSocket connection is working
- Try refreshing the page
- Make sure JavaScript is enabled
- Try a different browser

### C program can't connect
- Make sure web server is running first
- Check firewall settings
- Verify `WEB=1` was used when building

## Why Poetry?

1. **Isolated Environments**: Each project has its own virtual environment
2. **No System Conflicts**: Doesn't touch system Python
3. **Dependency Locking**: `poetry.lock` ensures reproducible builds
4. **Cross-platform**: Works the same on Windows, Linux, Mac
5. **Modern Standard**: Recommended by Python Packaging Authority

## Next Steps

Once setup is complete:
1. Start the simulator: `poetry run web-server` or `poetry run desktop-simulator`
2. Open browser (for web): http://localhost:5000
3. Build remote control: `make SIMULATOR=1 WEB=1`
4. Run remote control: `./bin/remote_control`
5. Press buttons and see them in the simulator!

That's it! Poetry handles everything.

