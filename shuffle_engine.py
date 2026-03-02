import datetime
from crypto_engine import hash_server_seed, generate_hmac_entropy, map_entropy_to_index
from log_engine import LogChain

def process_lottery(names, server_seed, client_seed, raw_entropy):
    log_chain = LogChain()
    ss_hash = hash_server_seed(server_seed)
    derived_hash = generate_hmac_entropy(server_seed, client_seed, 0, raw_entropy)
    winner_idx, large_int = map_entropy_to_index(derived_hash, len(names))
    
    log_chain.add_event(
        datetime.datetime.now(datetime.timezone.utc).isoformat(),
        ss_hash, client_seed, 0, raw_entropy, derived_hash, winner_idx,
        {"type": "lottery_selection", "winner": names[winner_idx], "math": f"Hash converted to Int: {large_int}. Modulo {len(names)} = {winner_idx}"}
    )
    return [names[winner_idx]], log_chain

def process_shuffle(names, server_seed, client_seed, raw_entropy):
    log_chain = LogChain()
    ss_hash = hash_server_seed(server_seed)
    nonce = 0
    arr = names.copy()
    n = len(arr)
    
    for i in range(n - 1, 0, -1):
        derived_hash = generate_hmac_entropy(server_seed, client_seed, nonce, raw_entropy)
        j, large_int = map_entropy_to_index(derived_hash, i + 1)
        arr[i], arr[j] = arr[j], arr[i]
        
        log_chain.add_event(
            datetime.datetime.now(datetime.timezone.utc).isoformat(),
            ss_hash, client_seed, nonce, raw_entropy, derived_hash, j,
            {"type": "shuffle_swap", "i": i, "j": j, "swap_values": f"{arr[j]} <-> {arr[i]}", "math": f"Int {str(large_int)[:10]}... Modulo {i+1} = {j}"}
        )
        nonce += 1
    return arr, log_chain

def process_weighted_shuffle(names_with_weights, server_seed, client_seed, raw_entropy):
    log_chain = LogChain()
    ss_hash = hash_server_seed(server_seed)
    nonce = 0
    results = []
    
    for item in names_with_weights:
        name = item['name']
        w = float(item['weight']) + 1.0  
        
        derived_hash = generate_hmac_entropy(server_seed, client_seed, nonce, raw_entropy)
        u = int(derived_hash, 16) / ((1 << 256) - 1)
        if u == 0: u = 1e-10
        score = u ** (1.0 / w)
        
        results.append({"name": name, "weight": item['weight'], "score": score, "hash": derived_hash})
        
        log_chain.add_event(
            datetime.datetime.now(datetime.timezone.utc).isoformat(),
            ss_hash, client_seed, nonce, raw_entropy, derived_hash, 0,
            {"type": "weighted_score", "name": name, "math": f"U={u:.6f}, W={w} -> Score={score:.6f}"}
        )
        nonce += 1
        
    results.sort(key=lambda x: x['score'])
    return [r['name'] for r in results], log_chain

def chunk_into_teams(lst, num_teams):
    teams = [[] for _ in range(num_teams)]
    for i, item in enumerate(lst): teams[i % num_teams].append(item)
    return teams

def chunk_into_pairs(lst):
    return [lst[i:i + 2] for i in range(0, len(lst), 2)]

# --- NEW 3-TIER CLASSROOM SEATING ---
def chunk_into_classroom(lst, t_rows, t_cols, seats_per_table):
    classroom = []
    idx = 0
    for r in range(t_rows):
        row_of_tables = []
        for c in range(t_cols):
            table = []
            for s in range(seats_per_table):
                table.append(lst[idx] if idx < len(lst) else "Empty Seat")
                idx += 1
            row_of_tables.append(table)
        classroom.append(row_of_tables)
    return classroom

# Legacy Support Functions
def chunk_into_rows_cols(lst, cols, rows):
    chart = []; idx = 0
    for r in range(rows):
        row = []
        for c in range(cols):
            row.append(lst[idx] if idx < len(lst) else "Empty Seat")
            idx += 1
        chart.append(row)
    return chart

def chunk_into_tables(lst, num_tables, seats_per_table):
    chart = []; idx = 0
    for t in range(num_tables):
        table = []
        for s in range(seats_per_table):
            table.append(lst[idx] if idx < len(lst) else "Empty Seat")
            idx += 1
        chart.append(table)
    return chart

def generate_bracket(lst):
    matchups = []
    for i in range(0, len(lst), 2):
        if i + 1 < len(lst): matchups.append({"p1": lst[i], "p2": lst[i+1]})
        else: matchups.append({"p1": lst[i], "p2": "BYE (Free Pass)"})
    return matchups

def apply_roles(lst, roles_str):
    roles = [r.strip() for r in roles_str.split(',') if r.strip()]
    return [{"name": lst[i], "role": roles[i] if i < len(roles) else "Participant"} for i in range(len(lst))]

def apply_secret_santa(lst):
    return [{"giver": lst[i], "receiver": lst[(i+1)%len(lst)]} for i in range(len(lst))]