from __future__ import annotations

import hashlib


def hash_api_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


def hash_ip(ip_address: str, salt: str) -> str:
    payload = f"{salt}:{ip_address}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
