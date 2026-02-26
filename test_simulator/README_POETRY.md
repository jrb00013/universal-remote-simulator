# Using Poetry for TV Simulator

This project uses [Poetry](https://python-poetry.org/) for dependency management.

## Quick Start

### 1. Install Poetry (if not already installed)

**Windows (PowerShell):**
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

**Mac/Linux:**
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

After installation, restart your terminal or add Poetry to PATH.

### 2. Install Dependencies

```bash
cd test_simulator
poetry install
```

This will:
- Create a virtual environment
- Install all dependencies (Flask, SocketIO, Pygame, etc.)
- Set up the project

### 3. Run the Simulator

**Web Server (3D/VR):**
```bash
poetry run web-server
# OR
poetry run python web_server.py
```

**Desktop Simulator:**
```bash
poetry run desktop-simulator
# OR
poetry run python main.py
```

## Poetry Commands

### Install dependencies
```bash
poetry install
```

### Add a new dependency
```bash
poetry add package-name
```

### Add a dev dependency
```bash
poetry add --group dev package-name
```

### Update dependencies
```bash
poetry update
```

### Show installed packages
```bash
poetry show
```

### Activate virtual environment shell
```bash
poetry shell
# Now you can run commands directly without 'poetry run'
python web_server.py
```

### Run commands in virtual environment
```bash
poetry run python script.py
poetry run pytest
```

### Export requirements.txt (for non-Poetry users)
```bash
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

## Project Structure

```
test_simulator/
├── pyproject.toml      # Poetry configuration
├── poetry.lock        # Locked dependencies (auto-generated)
├── web_server.py      # Web server entry point
├── main.py            # Desktop simulator entry point
└── ...
```

## Benefits of Poetry

1. **Dependency Management**: Automatic dependency resolution
2. **Virtual Environment**: Isolated environment per project
3. **Lock File**: Reproducible builds with `poetry.lock`
4. **Scripts**: Easy command aliases via `pyproject.toml`
5. **Cross-platform**: Works on Windows, Mac, Linux

## Migration from pip

If you were using `pip install -r requirements.txt`:

1. **Old way:**
   ```bash
   pip install -r requirements.txt
   python web_server.py
   ```

2. **New way (Poetry):**
   ```bash
   poetry install
   poetry run web-server
   ```

The `requirements.txt` file is still available for non-Poetry users, but Poetry is recommended.

## Troubleshooting

### Poetry command not found
- Make sure Poetry is installed
- Add Poetry to your PATH
- Restart terminal

### Virtual environment issues
```bash
poetry env remove python  # Remove existing env
poetry install            # Recreate it
```

### Lock file conflicts
```bash
poetry lock --no-update  # Update lock without updating packages
poetry install           # Install from lock
```

## Development

### Install dev dependencies
```bash
poetry install --with dev
```

### Run tests (when added)
```bash
poetry run pytest
```

### Format code (when black is configured)
```bash
poetry run black .
```

## CI/CD

For continuous integration, use:
```bash
poetry install --no-interaction --no-ansi
poetry run python web_server.py
```

