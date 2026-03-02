"""
Brand detection for universal remote: text -> TV brand.

Uses substring and word-boundary matching against a fixed keyword table (BRAND_KEYWORDS):
e.g. "samsung", "qled", "lg", "oled" etc. No external APIs, no embeddings, no models.
Returns brand name, brand_id (must match include/universal_tv.h tv_brand_t: 0=Unknown,
1=Samsung, 2=LG, ...), and a confidence derived from match length and word match.

Why revolutionary: In one codebase the simulator gets "user said Samsung" and the C remote
can set universal_tv_set_brand(SAMSUNG) with no cloud and no API keys—unique in open
universal-remote projects.
"""
import re

# Brand ID must match C: universal_tv.h tv_brand_t (0=UNKNOWN, 1=SAMSUNG, 2=LG, ...)
BRAND_IDS = {
    "unknown": 0,
    "samsung": 1,
    "lg": 2,
    "sony": 3,
    "philips": 4,
    "panasonic": 5,
    "tcl": 6,
    "vizio": 7,
    "hisense": 8,
    "toshiba": 9,
    "sharp": 10,
}

# Keywords and aliases per brand (lowercase)
BRAND_KEYWORDS = {
    "samsung": ["samsung", "galaxy tv", "qled", "the frame", "serif"],
    "lg": ["lg", "lg electronics", "oled", "nanocell", "webos"],
    "sony": ["sony", "bravia", "xbr", "a8", "x90"],
    "philips": ["philips", "philips tv", "ambilight"],
    "panasonic": ["panasonic", "viera", "gx", "hz"],
    "tcl": ["tcl", "tcl roku", "tcl android"],
    "vizio": ["vizio", "v-series", "m-series", "p-series"],
    "hisense": ["hisense", "u8", "u7", "a6"],
    "toshiba": ["toshiba", "toshiba tv", "c350", "c370"],
    "sharp": ["sharp", "aquos", "sharp tv"],
}


def detect_brand_from_text(text: str) -> dict:
    """
    Infer TV brand from free text (e.g. "I have a Samsung Q80", "LG C2").
    Returns dict: brand (str), brand_id (int), confidence (float 0..1).
    """
    if not text or not isinstance(text, str):
        return {"brand": "Unknown", "brand_id": 0, "confidence": 0.0}

    lower = text.lower().strip()
    best_brand = "unknown"
    best_score = 0

    for brand_name, keywords in BRAND_KEYWORDS.items():
        score = 0
        for kw in keywords:
            if kw in lower:
                # Prefer longer / more specific matches
                score += len(kw) + (2 if re.search(rf"\b{re.escape(kw)}\b", lower) else 0)
        if score > best_score:
            best_score = score
            best_brand = brand_name

    brand_id = BRAND_IDS.get(best_brand, 0)
    confidence = min(1.0, 0.3 + 0.7 * (best_score / 10.0)) if best_score else 0.0
    display_name = best_brand.capitalize() if best_brand != "unknown" else "Unknown"

    return {
        "brand": display_name,
        "brand_id": brand_id,
        "confidence": round(confidence, 2),
    }
