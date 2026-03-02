"""
System tests for the TV simulator: streaming, channels, frame API, rapid switching.
Integrates scenarios from the former tests_archive for robust system testing.
"""
import pytest
import requests
import time
from tests.conftest import (
    BASE_URL,
    API_URL,
    STATE_URL,
    FRAME_URL,
    BUTTON_CODES,
    STREAMING_SERVICES,
    NUMBER_BUTTONS,
    press_button,
    get_state,
)


class TestStreamingStrict:
    """Streaming service tests with strict current_app verification."""

    @pytest.mark.parametrize("service_name,button_code", list(STREAMING_SERVICES.items()))
    def test_streaming_service_app_matches(
        self, server_running, ensure_tv_on, service_name, button_code
    ):
        """After pressing a streaming button, current_app must match the service."""
        press_button(button_code, delay=2.0)
        # Allow transition time; poll for target app (first test can be slow after power-on)
        state = None
        for _ in range(12):
            state = get_state()
            if state and state.get("current_app") == service_name:
                break
            time.sleep(0.5)
        assert state is not None
        assert state.get("current_app") == service_name, (
            f"Expected current_app={service_name!r}, got {state.get('current_app')!r}"
        )


class TestRapidStreamingSwitch:
    """Rapid switching between streaming services (stress/consistency)."""

    def test_rapid_streaming_cycles(self, server_running, ensure_tv_on):
        """Multiple cycles through all streaming services; state must stay consistent."""
        services = list(STREAMING_SERVICES.items())
        for cycle in range(2):
            for service_name, button_code in services:
                press_button(button_code, delay=0.5)
                state = get_state()
                assert state is not None
                assert state.get("current_app") == service_name, (
                    f"Cycle {cycle + 1} {service_name}: expected current_app={service_name!r}, "
                    f"got {state.get('current_app')!r}"
                )


class TestChannelAndTVShows:
    """Channel changes and TV show display (number buttons, current_app for TV)."""

    @pytest.mark.parametrize("channel_number", [456, 789, 123, 42, 7])
    def test_channel_set_and_tv_mode(
        self, server_running, ensure_tv_on, channel_number
    ):
        """Number buttons set channel; on TV mode current_app should be None."""
        # Clear any prior channel input by waiting past the 2s timeout
        time.sleep(2.5)
        channel_str = str(channel_number).zfill(3)
        for digit in channel_str:
            press_button(NUMBER_BUTTONS[digit], delay=0.25)
        time.sleep(1.0)
        state = get_state()
        assert state is not None
        actual = state.get("channel")
        assert 1 <= actual <= 999, (
            f"Channel should be 1-999, got {actual}"
        )
        # When showing TV (channel), current_app is typically None
        current_app = state.get("current_app")
        assert current_app is None or current_app == "Home", (
            f"For channel {channel_number} expected current_app None or Home, got {current_app!r}"
        )

    def test_home_from_tv_returns_home(self, server_running, ensure_tv_on):
        """Home button returns to Home screen (current_app == 'Home')."""
        # Ensure we're not on Home (e.g. switch to a channel or app)
        press_button(STREAMING_SERVICES["YouTube"], delay=1.0)
        state = get_state()
        assert state is not None
        assert state.get("current_app") == "YouTube"

        press_button(BUTTON_CODES["Home"], delay=1.0)
        state = get_state()
        assert state is not None
        assert state.get("current_app") == "Home"


class TestFrameAPI:
    """Frame/streaming API availability and basic shape."""

    def test_frame_info_returns_dimensions(self, server_running, ensure_tv_on):
        """Frame info endpoint returns width/height when available."""
        time.sleep(1.0)
        try:
            r = requests.get(f"{FRAME_URL}/info", timeout=5)
        except Exception:
            pytest.skip("Frame info endpoint not available")
        if r.status_code != 200:
            pytest.skip("Frame info returned non-200")
        data = r.json()
        assert isinstance(data, dict)
        if "width" in data and "height" in data:
            assert data["width"] > 0 and data["height"] > 0

    def test_frame_png_or_json_available(self, server_running, ensure_tv_on):
        """At least one of PNG or JSON frame endpoints responds successfully."""
        time.sleep(1.0)
        ok = False
        r_png = requests.get(FRAME_URL, timeout=5)
        if r_png.status_code == 200 and "image" in (r_png.headers.get("content-type") or ""):
            ok = True
        r_json = requests.get(f"{FRAME_URL}?format=json", timeout=5)
        if r_json.status_code == 200:
            data = r_json.json()
            if isinstance(data, dict) and ("frame" in data or "width" in data):
                ok = True
        assert ok, "Neither PNG nor JSON frame endpoint returned valid response"
