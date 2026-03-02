"""
Tests for protocol_classifier module (pulse-length list -> protocol ID).

Rule-based threshold matching only. See docs/ML_CV_AI_AUDIT.md.
"""
import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestProtocolClassifierApiSurface:
    """Module exposes rule-based API only; no model or predict."""

    def test_no_model_or_predict(self):
        import protocol_classifier as m
        assert not hasattr(m, "model")
        assert not hasattr(m, "predict")

    def test_public_api(self):
        import protocol_classifier as m
        assert hasattr(m, "classify_protocol")
        assert hasattr(m, "evaluate_rule_based_classifier")
        assert hasattr(m, "load_synthetic_dataset")


class TestProtocolClassifierResponse:
    """Output shape and value constraints."""

    def test_response_shape(self):
        from protocol_classifier import classify_protocol
        from ir_synthetic import nec_code_to_timings
        r = classify_protocol(nec_code_to_timings(0x20DF10EF))
        assert "protocol" in r and "protocol_id" in r and "confidence" in r
        assert isinstance(r["protocol"], str)
        assert isinstance(r["protocol_id"], int)
        assert isinstance(r["confidence"], (int, float))


class TestProtocolClassifierNec:
    """NEC protocol: 9ms / 4.5ms leader."""

    def test_identified_by_leader(self):
        from protocol_classifier import classify_protocol
        from ir_synthetic import nec_code_to_timings
        r = classify_protocol(nec_code_to_timings(0x20DF10EF))
        assert r["protocol"] == "NEC"
        assert r["protocol_id"] == 1

    def test_tolerance_within_40_percent(self):
        from protocol_classifier import classify_protocol
        r = classify_protocol([9000 * 0.85, 4500 * 0.85, 560, 560])
        assert r["protocol"] == "NEC"


class TestProtocolClassifierRc5:
    """RC5 protocol: repeated 889 us (no long leader)."""

    def test_identified_by_889_pattern(self):
        from protocol_classifier import classify_protocol
        from ir_synthetic import rc5_code_to_timings
        r = classify_protocol(rc5_code_to_timings(0x0C))
        assert r["protocol"] == "RC5"
        assert r["protocol_id"] == 2


class TestProtocolClassifierRc6:
    """RC6 protocol: 2666 us / 889 us leader."""

    def test_identified_by_leader(self):
        from protocol_classifier import classify_protocol
        from ir_synthetic import rc6_code_to_timings
        r = classify_protocol(rc6_code_to_timings(0x800F040C))
        assert r["protocol"] == "RC6"
        assert r["protocol_id"] == 3


class TestProtocolClassifierUnknown:
    """Short or invalid input -> unknown."""

    def test_short_list(self):
        from protocol_classifier import classify_protocol
        r = classify_protocol([100, 200])
        assert r["protocol"] == "unknown"
        assert r["protocol_id"] == 0

    def test_empty_list(self):
        from protocol_classifier import classify_protocol
        r = classify_protocol([])
        assert r["protocol_id"] == 0


class TestProtocolClassifierEvaluate:
    """evaluate_rule_based_classifier on synthetic dataset."""

    def test_returns_total_correct_accuracy(self):
        from ir_synthetic import generate_dataset
        from protocol_classifier import evaluate_rule_based_classifier
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            path = f.name
        try:
            generate_dataset(30, path)
            stats = evaluate_rule_based_classifier(path)
            assert stats["total"] > 0
            assert "correct" in stats
            assert "accuracy" in stats
            assert stats["accuracy"] >= 0.5
        finally:
            if os.path.exists(path):
                os.unlink(path)
