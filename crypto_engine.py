import hashlib
import hmac
import secrets
import json

def generate_server_seed() -> str:
    return secrets.token_hex(32)

def hash_server_seed(seed: str) -> str:
    return hashlib.sha256(seed.encode('utf-8')).hexdigest()

def generate_hmac_entropy(server_seed: str, client_seed: str, nonce: int, external_entropy: str) -> str:
    message = f"{client_seed}:{nonce}:{external_entropy}"
    return hmac.new(server_seed.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).hexdigest()

def map_entropy_to_index(hmac_hex: str, max_val: int) -> tuple[int, int]:
    large_int = int(hmac_hex, 16)
    return large_int % max_val, large_int

def constant_time_compare(val1: str, val2: str) -> bool:
    return hmac.compare_digest(str(val1), str(val2))

def get_deterministic_json(data_dict: dict) -> str:
    return json.dumps(data_dict, sort_keys=True, separators=(',', ':'))

def compute_file_seal(data_dict: dict) -> str:
    clean_data = {k: v for k, v in data_dict.items() if k not in ['final_file_seal']}
    return hashlib.sha256(get_deterministic_json(clean_data).encode('utf-8')).hexdigest()

def compute_signature(data_dict: dict, password: str) -> str:
    clean_data = {k: v for k, v in data_dict.items() if k not in ['final_file_seal', 'signature']}
    return hmac.new(password.encode('utf-8'), get_deterministic_json(clean_data).encode('utf-8'), hashlib.sha256).hexdigest()