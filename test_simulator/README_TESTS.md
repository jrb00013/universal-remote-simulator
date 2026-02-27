# Test Suite

This directory contains a comprehensive pytest test suite for the Virtual TV Simulator.

## Running Tests

### Run All Tests

```bash
# Make sure server is running first
poetry run web-server

# In another terminal, run tests
poetry run pytest
```

### Run Specific Test Categories

```bash
# Unit tests only (no server required)
poetry run pytest tests/test_unit.py

# API tests (requires server)
poetry run pytest tests/test_api.py

# Functional tests (requires server)
poetry run pytest tests/test_functional.py

# All button tests
poetry run pytest tests/test_all_buttons.py
```

### Run with Verbose Output

```bash
poetry run pytest -v
```

### Run Specific Test

```bash
poetry run pytest tests/test_api.py::TestButtonAPI::test_power_button
```

## Test Structure

```
tests/
├── __init__.py
├── conftest.py          # Shared fixtures and configuration
├── test_unit.py         # Unit tests (no server required)
├── test_api.py          # REST API integration tests
├── test_functional.py   # Functional workflow tests
└── test_all_buttons.py  # Test all button codes
```

## Test Categories

### Unit Tests (`test_unit.py`)
- Module imports
- File structure
- Python syntax
- HTML structure
- JavaScript structure

**No server required** - These tests can run without the web server.

### API Tests (`test_api.py`)
- Server connection
- REST API endpoints
- Button press API
- Streaming/frame API
- State consistency

**Requires server** - Server must be running (`poetry run web-server`).

### Functional Tests (`test_functional.py`)
- Power cycle
- Streaming services
- Channel changes
- Navigation
- Volume control
- WebSocket functionality

**Requires server** - Server must be running.

### All Buttons Tests (`test_all_buttons.py`)
- Tests every button code individually

**Requires server** - Server must be running.

## Fixtures

### `server_running`
Checks if server is running, skips tests if not.

### `tv_state`
Gets current TV state.

### `ensure_tv_on`
Ensures TV is powered on before test, turns it off after.

## Helper Functions

### `press_button(button_code, delay=0.5)`
Presses a button via API and waits.

### `get_state()`
Gets current TV state from API.

## Configuration

Test configuration is in `pytest.ini`:
- Test paths
- Output verbosity
- Markers for test categorization

## Continuous Integration

To run tests in CI:

```bash
# Start server in background
poetry run web-server &
sleep 5  # Wait for server to start

# Run tests
poetry run pytest

# Stop server
pkill -f web-server
```

## Troubleshooting

### Tests fail with "Server is not running"
Start the server first:
```bash
poetry run web-server
```

### Tests timeout
Increase timeout in `conftest.py` or check server is responding.

### Some tests are skipped
Check if server is running and accessible at `http://localhost:5000`.

