"""
Tests for ir_synthetic module (synthetic IR pulse-length generation).

Uses same timing constants as C (ir_protocol.c). See docs/ML_CV_AI_AUDIT.md.
"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestIrSyntheticNec:
    """NEC: leader 9ms / 4.5ms, then 32 bits."""

    def test_leader_timings(self):
        from ir_synthetic import nec_code_to_timings
        t = nec_code_to_timings(0x20DF10EF)
        assert t[0] == 9000 and t[1] == 4500

    def test_length_leader_plus_32_bits(self):
        from ir_synthetic import nec_code_to_timings
        t = nec_code_to_timings(0x20DF10EF)
        assert len(t) == 2 + 32 * 2


class TestIrSyntheticRc5:
    """RC5: 14 bits, 889 us per half-bit."""

    def test_all_889(self):
        from ir_synthetic import rc5_code_to_timings
        t = rc5_code_to_timings(0x10, bits=14)
        assert len(t) == 14 * 2
        assert all(x == 889 for x in t)


class TestIrSyntheticRc6:
    """RC6: leader 2666 / 889, then 20 bits of 444 us."""

    def test_leader_and_length(self):
        from ir_synthetic import rc6_code_to_timings
        t = rc6_code_to_timings(0x800F040C)
        assert t[0] == 2666 and t[1] == 889
        assert len(t) == 2 + 20 * 2


class TestIrSyntheticGenerateDataset:
    """generate_dataset output format and content."""

    def test_contains_all_three_protocols(self):
        from ir_synthetic import generate_dataset
        data = generate_dataset(5, output_path=None)
        protocols = {s["protocol"] for s in data}
        assert "NEC" in protocols and "RC5" in protocols and "RC6" in protocols

    def test_each_entry_has_timings_us_protocol_protocol_id(self):
        from ir_synthetic import generate_dataset
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            path = f.name
        try:
            generate_dataset(3, path)
            with open(path) as f:
                data = json.load(f)
            for s in data:
                assert "timings_us" in s
                assert "protocol" in s
                assert "protocol_id" in s
                assert isinstance(s["timings_us"], list)
                assert all(isinstance(x, (int, float)) for x in s["timings_us"])
        finally:
            if os.path.exists(path):
                os.unlink(path)
