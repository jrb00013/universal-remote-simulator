"""
Tests for brand_detection module (text -> TV brand).

Rule-based keyword matching only. See docs/ML_CV_AI_AUDIT.md.
"""
import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestBrandDetectionApiSurface:
    """Module exposes keyword-based API only; no model or predict."""

    def test_no_model_or_predict(self):
        import brand_detection as m
        assert not hasattr(m, "model")
        assert not hasattr(m, "predict")

    def test_public_api(self):
        import brand_detection as m
        assert hasattr(m, "detect_brand_from_text")
        assert hasattr(m, "BRAND_KEYWORDS")
        assert hasattr(m, "BRAND_IDS")


class TestBrandDetectionResponse:
    """Output shape and value constraints."""

    def test_response_shape(self):
        from brand_detection import detect_brand_from_text
        r = detect_brand_from_text("Samsung")
        assert "brand" in r and "brand_id" in r and "confidence" in r
        assert isinstance(r["brand"], str)
        assert isinstance(r["brand_id"], int)
        assert isinstance(r["confidence"], (int, float))

    def test_confidence_in_range(self):
        from brand_detection import detect_brand_from_text
        for text in ["Samsung Q80", "LG OLED", "", "gibberish"]:
            r = detect_brand_from_text(text)
            assert 0 <= r["confidence"] <= 1.0


class TestBrandDetectionUnknown:
    """Empty or unrecognized input -> brand_id 0."""

    def test_empty_string(self):
        from brand_detection import detect_brand_from_text
        r = detect_brand_from_text("")
        assert r["brand_id"] == 0
        assert r["confidence"] == 0.0

    def test_gibberish(self):
        from brand_detection import detect_brand_from_text
        r = detect_brand_from_text("xyz qwerty")
        assert r["brand_id"] == 0


class TestBrandDetectionBrands:
    """All supported brands (BRAND_IDS) resolve correctly."""

    @pytest.mark.parametrize("text,expected_brand_id", [
        ("Samsung Q80", 1),
        ("LG OLED C2", 2),
        ("Sony Bravia", 3),
        ("Philips Ambilight", 4),
        ("Panasonic Viera", 5),
        ("TCL Roku", 6),
        ("Vizio M-series", 7),
        ("Hisense U8", 8),
        ("Toshiba TV", 9),
        ("Sharp Aquos", 10),
    ])
    def test_brand_id_and_confidence(self, text, expected_brand_id):
        from brand_detection import detect_brand_from_text
        r = detect_brand_from_text(text)
        assert r["brand_id"] == expected_brand_id
        assert r["confidence"] > 0
