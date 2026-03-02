import hashlib
import json
import time
import datetime

class LogChain:
    def __init__(self):
        self.chain = []
        self.last_hash = "0" * 64
        self.start_time = time.perf_counter()
        self.hash_count = 0

    def add_event(self, timestamp, server_seed_hash, client_seed, nonce, raw_entropy, derived_hash, selected_index, action_details):
        self.hash_count += 1
        event_data = {
            "timestamp": timestamp, "server_seed_hash": server_seed_hash, 
            "client_seed": client_seed, "nonce": nonce, 
            "raw_entropy": raw_entropy, "derived_hash": derived_hash, 
            "selected_index": selected_index, "action_details": action_details
        }
        event_json = json.dumps(event_data, sort_keys=True, separators=(',', ':'))
        current_hash = hashlib.sha256((self.last_hash + event_json).encode('utf-8')).hexdigest()
        
        self.chain.append({"previous_hash": self.last_hash, "event": event_data, "current_hash": current_hash})
        self.last_hash = current_hash
        
    def get_stats(self):
        return {"total_computations": self.hash_count, "execution_time_ms": round((time.perf_counter() - self.start_time) * 1000, 3)}
        
    def export(self):
        return self.chain

def create_ledger_block(title: str, notes: str, author: str, prev_hash: str) -> dict:
    block = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "title": title, "notes": notes, "author": author, "previous_hash": prev_hash
    }
    block_str = json.dumps(block, sort_keys=True, separators=(',', ':'))
    block['block_hash'] = hashlib.sha256(block_str.encode('utf-8')).hexdigest()
    return block