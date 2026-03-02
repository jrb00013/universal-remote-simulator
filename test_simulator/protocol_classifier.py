"""
IR protocol classifier: list of pulse lengths (µs, alternating mark/space) -> protocol ID.

Implementation is rule-based only. We check the first one or two timings against known
leader patterns (from ir_protocol.c / NEC/RC5/RC6 specs):
  - First pair 9000µs, 4500µs (±40% tol) -> NEC.
  - First pair 2666µs, 889µs -> RC6.
  - First value ~889µs and several of the next ~889µs -> RC5 (no long leader).

No neural nets, no training. classify_protocol(timings_us) returns protocol name, protocol_id
(1=NEC, 2=RC5, 3=RC6, 0=unknown), and a confidence float. load_synthetic_dataset /
evaluate_rule_based_classifier use the JSON from ir_synthetic.generate_dataset() to
measure accuracy of these rules on synthetic data.

Why revolutionary: Protocol is identified from raw timing using the same constants as the
C encoder. No other open universal-remote stack has timing-based protocol classification
and the encoder sharing one spec in one repo—enables "one capture -> know protocol" with
zero external services.
"""
import os
import json

# Protocol IDs (match C and synthetic dataset)
PROTOCOL_NEC = 1
PROTOCOL_RC5 = 2
PROTOCOL_RC6 = 3
PROTOCOL_UNKNOWN = 0

# Timing tolerances (µs) — real captures have jitter
TOL = 0.4  # 40% tolerance
NEC_LEADER_PULSE = 9000
NEC_LEADER_SPACE = 4500
RC5_BIT = 889
RC6_LEADER_PULSE = 2666
RC6_LEADER_SPACE = 889
RC6_BIT = 444


def _in_range(val: float, ref: int, tol: float = TOL) -> bool:
    return ref * (1 - tol) <= val <= ref * (1 + tol)


def classify_protocol(timings_us: list) -> dict:
    """
    Classify IR protocol from list of pulse lengths (alternating mark/space in µs).
    Returns {"protocol": "NEC"|"RC5"|"RC6"|"unknown", "protocol_id": int, "confidence": float}.
    """
    if not timings_us or len(timings_us) < 4:
        return {"protocol": "unknown", "protocol_id": PROTOCOL_UNKNOWN, "confidence": 0.0}

    first = timings_us[0]
    second = timings_us[1] if len(timings_us) > 1 else 0

    # NEC: 9ms pulse, 4.5ms space
    if _in_range(first, NEC_LEADER_PULSE) and _in_range(second, NEC_LEADER_SPACE):
        return {"protocol": "NEC", "protocol_id": PROTOCOL_NEC, "confidence": 0.9}

    # RC6: 2.666ms pulse, 889µs space
    if _in_range(first, RC6_LEADER_PULSE) and _in_range(second, RC6_LEADER_SPACE):
        return {"protocol": "RC6", "protocol_id": PROTOCOL_RC6, "confidence": 0.9}

    # RC5: no long leader; ~889µs repeated (Manchester)
    if _in_range(first, RC5_BIT):
        # Check a few more to confirm ~889 pattern
        count_889 = sum(1 for t in timings_us[:20] if _in_range(t, RC5_BIT))
        if count_889 >= 4:
            return {"protocol": "RC5", "protocol_id": PROTOCOL_RC5, "confidence": 0.85}

    return {"protocol": "unknown", "protocol_id": PROTOCOL_UNKNOWN, "confidence": 0.0}


def load_synthetic_dataset(path: str = None) -> list:
    """Load ir_dataset_synthetic.json (from ir_synthetic.generate_dataset) for evaluate_rule_based_classifier or other use."""
    if path is None:
        path = os.path.join(os.path.dirname(__file__), "ir_dataset_synthetic.json")
    if not os.path.isfile(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_rule_based_classifier(dataset_path: str = None) -> dict:
    """Run rule-based classifier on synthetic dataset; return accuracy."""
    data = load_synthetic_dataset(dataset_path)
    if not data:
        return {"accuracy": 0.0, "total": 0}
    correct = 0
    for sample in data:
        pred = classify_protocol(sample["timings_us"])
        if pred["protocol_id"] == sample.get("protocol_id", 0):
            correct += 1
    return {"accuracy": correct / len(data), "total": len(data), "correct": correct}
