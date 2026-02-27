"""
Test all button codes
"""
import pytest
import time
from tests.conftest import BUTTON_CODES, press_button, get_state, server_running


class TestAllButtons:
    """Test all available button codes"""
    
    @pytest.mark.parametrize("button_name,button_code", [
        ('Power', 0x10),
        ('Volume Up', 0x11),
        ('Volume Down', 0x12),
        ('Mute', 0x13),
        ('Channel Up', 0x14),
        ('Channel Down', 0x15),
        ('Home', 0x20),
        ('Menu', 0x21),
        ('Back', 0x22),
        ('Info', 0x23),
        ('YouTube', 0x01),
        ('Netflix', 0x02),
        ('Amazon Prime', 0x03),
        ('HBO Max', 0x04),
        ('Game Mode', 0xA0),
        ('Input', 0x25),
        ('Source', 0x26),
    ])
    def test_button_code(self, server_running, button_name, button_code):
        """Test each button code"""
        # Press button
        success = press_button(button_code, delay=0.3)
        assert success is True
        
        # Verify state is still accessible
        state = get_state()
        assert state is not None

