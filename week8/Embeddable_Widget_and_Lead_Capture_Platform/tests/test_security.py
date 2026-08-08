from app.core.security import hash_api_key, hash_ip

def test_api_key_hash_is_deterministic_and_not_plaintext():
    raw="secret-key"
    assert hash_api_key(raw) == hash_api_key(raw)
    assert hash_api_key(raw) != raw

def test_ip_hash_changes_with_salt():
    assert hash_ip("8.8.8.8", "a") != hash_ip("8.8.8.8", "b")
