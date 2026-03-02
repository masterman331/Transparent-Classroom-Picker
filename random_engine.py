import secrets
import requests
import time
import os
import platform
import threading
import hashlib
from config import Config

def get_entropy(source: str) -> tuple[str, dict]:
    start_time = time.perf_counter()
    if source == 'random_org':
        try:
            payload = {
                "jsonrpc": "2.0", 
                "method": "generateBlobs", 
                "params": {"apiKey": Config.RANDOM_ORG_API_KEY, "n": 1, "size": Config.ENTROPY_BYTES_REQUESTED, "format": "hex"}, 
                "id": 1
            }
            res = requests.post(Config.RANDOM_ORG_URL, json=payload, timeout=3)
            res.raise_for_status()
            data = res.json()
            if 'error' not in data:
                return data['result']['random']['data'][0], {
                    "source": "Random.org API", 
                    "latency_ms": round((time.perf_counter()-start_time)*1000, 2)
                }
        except Exception as e:
            print(f"Random.org Failed: {e}. Falling back to deep local entropy.")

    os_urandom = secrets.token_hex(Config.ENTROPY_BYTES_REQUESTED)
    sys_state = {
        "os_urandom_hex": os_urandom,
        "system_time_epoch": time.time(),
        "cpu_perf_counter": time.perf_counter(),
        "process_id": os.getpid(),
        "thread_id": threading.get_native_id() if hasattr(threading, 'get_native_id') else threading.get_ident(),
        "hostname": platform.node(),
        "os_info": platform.platform()
    }
    
    raw_mix = f"{sys_state}"
    final_hash = hashlib.sha256(raw_mix.encode()).hexdigest()[:Config.ENTROPY_BYTES_REQUESTED*2]
    
    return final_hash, {
        "source": "Local System Hybrid (Deep Variables)",
        "latency_ms": round((time.perf_counter() - start_time) * 1000, 2),
        "system_variables_used": sys_state
    }

def generate_client_seed() -> str:
    return secrets.token_hex(8)