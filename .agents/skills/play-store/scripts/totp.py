#!/usr/bin/env python3
"""Print the current TOTP code for a base32 secret read from stdin."""

import base64
import hashlib
import hmac
import struct
import sys
import time


def totp(secret: str, step: int = 30, digits: int = 6) -> str:
    compact = "".join(secret.split()).upper()
    pad = "=" * ((8 - len(compact) % 8) % 8)
    key = base64.b32decode(compact + pad, casefold=True)
    counter = int(time.time()) // step
    digest = hmac.new(key, struct.pack(">Q", counter), hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    code = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
    return str(code % 10**digits).zfill(digits)


if __name__ == "__main__":
    raw = sys.stdin.read()
    if not raw.strip():
        sys.exit("no 2FA token on stdin")
    sys.stdout.write(totp(raw))
