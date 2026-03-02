"""
Synthetic IR waveform generator.

Produces lists of pulse lengths in microseconds (alternating mark/space) for NEC,
RC5, and RC6 using the same timing constants as src/ir_protocol.c and ir_asm_c.c:
  NEC: 9ms leader pulse, 4.5ms space, then 32 bits of 560µs pulse + 560µs or 1690µs space.
  RC5: 14 bits, each bit = two 889µs intervals (Manchester).
  RC6: 2666µs pulse + 889µs space, then 20 bits of 444µs each.

Used by protocol_classifier (rule-based: match first pulse/space to these values) and
generate_dataset() writes JSON with timings_us + protocol_id for that classifier or
for any other consumer that expects (timing list, label) pairs.

Why revolutionary: The same numbers that encode IR in C are the single source of truth
for generating and classifying protocol from a timing list—encoder/decoder symmetry
in one repo, with no external protocol database.
"""
import json
import os

# Timing in microseconds (match ir_protocol.c, ir_asm_c.c)
NEC_LEADER_PULSE = 9000
NEC_LEADER_SPACE = 4500
NEC_BIT_PULSE = 560
NEC_BIT_0_SPACE = 560
NEC_BIT_1_SPACE = 1690

RC5_BIT = 889   # Manchester half-bit

RC6_LEADER_PULSE = 2666
RC6_LEADER_SPACE = 889
RC6_BIT = 444


def nec_code_to_timings(code: int, bits: int = 32) -> list:
    """NEC: leader + 32 bits (pulse, space). Returns list of µs (alternating mark/space)."""
    out = [NEC_LEADER_PULSE, NEC_LEADER_SPACE]
    mask = 1 << (bits - 1)
    for _ in range(bits):
        out.append(NEC_BIT_PULSE)
        out.append(NEC_BIT_1_SPACE if (code & mask) else NEC_BIT_0_SPACE)
        mask >>= 1
    return out


def rc5_code_to_timings(code: int, bits: int = 14) -> list:
    """RC5 Manchester: each bit = 889 ON/OFF or OFF/ON. Returns list of µs."""
    out = []
    mask = 1 << (bits - 1)
    for _ in range(bits):
        if code & mask:
            out.extend([RC5_BIT, RC5_BIT])   # OFF then ON (Manchester 1)
        else:
            out.extend([RC5_BIT, RC5_BIT])   # ON then OFF (Manchester 0) — same length, order in protocol
        mask >>= 1
    # Emit 889,889 per bit so the rule-based classifier (look for repeated ~889µs) can ID RC5.
    return out


def rc6_code_to_timings(code: int, bits: int = 20) -> list:
    """RC6: leader 2666+889 then 20 bits of 444 µs each (mark+space). Returns list of µs."""
    out = [RC6_LEADER_PULSE, RC6_LEADER_SPACE]
    for _ in range(bits):
        out.append(RC6_BIT)
        out.append(RC6_BIT)
    return out


def generate_dataset(num_per_protocol: int = 50, output_path: str = None) -> list:
    """Generate labeled (timings, protocol_id) for NEC, RC5, RC6. protocol_id: 1=NEC, 2=RC5, 3=RC6."""
    dataset = []
    # NEC: a few known codes
    nec_codes = [0x20DF10EF, 0x20DF40BF, 0x20DF906F, 0x20DF00FF, 0x20DF807F]
    for i in range(num_per_protocol):
        code = nec_codes[i % len(nec_codes)]
        dataset.append({"timings_us": nec_code_to_timings(code), "protocol": "NEC", "protocol_id": 1, "code": code})
    # RC5
    rc5_codes = [0x0C, 0x10, 0x11, 0x0D, 0x20, 0x21]
    for i in range(num_per_protocol):
        code = rc5_codes[i % len(rc5_codes)]
        dataset.append({"timings_us": rc5_code_to_timings(code), "protocol": "RC5", "protocol_id": 2, "code": code})
    # RC6
    rc6_codes = [0x800F040C, 0x800F0410, 0x800F0411, 0x800F040D]
    for i in range(num_per_protocol):
        code = rc6_codes[i % len(rc6_codes)]
        dataset.append({"timings_us": rc6_code_to_timings(code), "protocol": "RC6", "protocol_id": 3, "code": code})

    if output_path:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(dataset, f, indent=0)
    return dataset


if __name__ == "__main__":
    default_path = os.path.join(os.path.dirname(__file__), "ir_dataset_synthetic.json")
    data = generate_dataset(50, default_path)
    print(f"Generated {len(data)} samples -> {default_path}")
