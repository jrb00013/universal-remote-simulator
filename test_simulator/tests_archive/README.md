# Archived Test Files

These are the old test files that have been replaced by the pytest test suite in `tests/`.

The new pytest test suite provides:
- Better organization
- Proper fixtures and setup
- Integration with pytest ecosystem
- Better reporting
- Easier to maintain and extend

## Old Test Files

- `test_all.py` - Comprehensive test script (replaced by `tests/test_unit.py`)
- `test_interactive_3d.py` - Interactive 3D tests (replaced by `tests/test_functional.py` and `tests/test_api.py`)
- `test_streaming_simple.py` - Simple streaming tests (replaced by `tests/test_functional.py::TestStreamingServices`)
- `test_streaming_auto.py` - Automated streaming tests (replaced by `tests/test_functional.py::TestStreamingServices`)
- `test_streaming.py` - Streaming tests (replaced by `tests/test_functional.py::TestStreamingServices`)
- `test_channel_tv_shows.py` - Channel tests (replaced by `tests/test_functional.py::TestChannelChanges`)
- `test_standalone.py` - Standalone test (functionality preserved in pytest suite)

## Migration

All functionality from these old tests has been migrated to the pytest suite:
- Unit tests → `tests/test_unit.py`
- API tests → `tests/test_api.py`
- Functional tests → `tests/test_functional.py`
- Button tests → `tests/test_all_buttons.py`

## Running New Tests

```bash
# Run all tests
poetry run pytest

# Run specific test categories
poetry run pytest tests/test_unit.py
poetry run pytest tests/test_api.py
poetry run pytest tests/test_functional.py
```

See `README_TESTS.md` for complete documentation.

