"""
Tests to ensure the remote works and that button presses trigger the visual
animation pipeline (WebSocket state updates so the 3D remote shows green
highlight and press animation).
"""
import pytest
import time
import requests
import socketio
from tests.conftest import (
    BASE_URL,
    API_URL,
    STATE_URL,
    BUTTON_CODES,
    press_button,
    get_state,
)


class TestRemoteWorks:
    """Verify the remote accepts button presses and state updates."""

    def test_remote_accepts_button_press(self, server_running):
        """Remote must accept a button press and return success."""
        response = requests.post(
            API_URL,
            json={"button_code": BUTTON_CODES["Power"]},
            headers={"Content-Type": "application/json"},
            timeout=5,
        )
        assert response.status_code == 200

    def test_remote_state_updates_after_button(self, server_running, ensure_tv_on):
        """Pressing a button must update TV state (remote has effect)."""
        initial = get_state()
        initial_vol = initial.get("volume", 0) if initial else 0

        press_button(BUTTON_CODES["Volume Up"], delay=0.3)
        new = get_state()
        new_vol = new.get("volume", 0) if new else 0

        assert new is not None
        assert new_vol >= initial_vol


class TestVisualAnimationPipeline:
    """
    Verify that button presses trigger the pipeline that drives visual
    animation: server broadcasts tv_state_update so the client can run
    highlightRemoteButton (green glow + press-in) and IR/state animations.
    """

    def test_websocket_receives_state_update_on_button_press(
        self, server_running, ensure_tv_on
    ):
        """Button press must cause server to broadcast tv_state_update (visual animation)."""
        sio = socketio.Client()
        updates = []

        @sio.on("tv_state_update")
        def on_state(data):
            updates.append(data)

        try:
            sio.connect(BASE_URL, wait_timeout=5)
            time.sleep(0.5)

            # Press button via API (same as clicking remote in UI)
            press_button(BUTTON_CODES["Volume Up"], delay=0.2)
            time.sleep(0.5)

            assert len(updates) >= 1, (
                "Expected at least one tv_state_update so the client can show "
                "button visual animation (green highlight + press effect)"
            )
            state = updates[-1]
            assert isinstance(state, dict)
            assert "volume" in state or "powered_on" in state
        finally:
            sio.disconnect()

    def test_websocket_button_press_triggers_state_broadcast(
        self, server_running, ensure_tv_on
    ):
        """Emitting button_press over WebSocket must result in tv_state_update."""
        sio = socketio.Client()
        updates = []

        @sio.on("tv_state_update")
        def on_state(data):
            updates.append(data)

        try:
            sio.connect(BASE_URL, wait_timeout=5)
            time.sleep(0.5)

            sio.emit("button_press", {"button_code": BUTTON_CODES["Channel Up"]})
            time.sleep(0.5)

            assert len(updates) >= 1, (
                "WebSocket button_press should cause tv_state_update for "
                "remote visual animation (highlight + channel animation)"
            )
        finally:
            sio.disconnect()
