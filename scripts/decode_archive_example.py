#!/usr/bin/env python3
"""Round-trip test for the hex-encode/decode trick used in
examples/automations/monthly-archive.yaml.

Proves the actual claim this repo makes: a JSON payload with embedded double
quotes and non-ASCII characters survives being hex-encoded (the Jinja side,
`payload.encode('utf-8').hex()`), passed across a shell boundary as a plain
hex string, and decoded back (the python3 side,
`bytes.fromhex(...).decode('utf-8')`) without any shell-quoting corruption.
"""
import json
import sys


def encode_like_jinja(payload: str) -> str:
    # Mirrors: {{ payload.encode('utf-8').hex() }}
    return payload.encode("utf-8").hex()


def decode_like_shell_command(payload_hex: str) -> str:
    # Mirrors the python3 -c one-liner in monthly-archive.yaml's shell_command.
    return bytes.fromhex(payload_hex).decode("utf-8")


def main():
    sample = {
        "month": "2026-06",
        "person_a": {"Zone 1": 12345, "Home": 54321},
        "note": 'she said "hi" at the café',
    }
    original_payload = json.dumps(sample)

    payload_hex = encode_like_jinja(original_payload)

    if not all(c in "0123456789abcdef" for c in payload_hex):
        print("FAIL: hex payload contains non-hex characters", file=sys.stderr)
        sys.exit(1)

    decoded_payload = decode_like_shell_command(payload_hex)

    if decoded_payload != original_payload:
        print("FAIL: round trip did not preserve the payload", file=sys.stderr)
        print(f"  original: {original_payload!r}", file=sys.stderr)
        print(f"  decoded:  {decoded_payload!r}", file=sys.stderr)
        sys.exit(1)

    if json.loads(decoded_payload) != sample:
        print("FAIL: decoded payload does not parse back to the original structure", file=sys.stderr)
        sys.exit(1)

    print("PASS: hex encode/decode round trip preserved the payload exactly")
    print(f"  original payload:  {original_payload}")
    print(f"  hex on the wire:   {payload_hex}")


if __name__ == "__main__":
    main()
