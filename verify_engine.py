import json
import hashlib
from crypto_engine import hash_server_seed, generate_hmac_entropy, map_entropy_to_index, constant_time_compare, compute_file_seal, compute_signature
from shuffle_engine import chunk_into_teams, chunk_into_pairs, apply_roles, apply_secret_santa, chunk_into_rows_cols, chunk_into_tables, chunk_into_classroom, generate_bracket

def verify_file_data(data: dict, input_password: str = "") -> tuple[bool, list, str]:
    audit_trail = []
    
    try:
        expected_seal = compute_file_seal(data)
        if not constant_time_compare(expected_seal, data.get('final_file_seal', '')):
            audit_trail.append({"step": 1, "status": "FAIL", "title": "Global File Seal (Zero-Tamper Check)", "desc": "File structure or data was altered.", "math": f"Expected: {expected_seal}"})
            return False, audit_trail, "CRITICAL TAMPER DETECTED: File structure or data was altered."
        audit_trail.append({"step": 1, "status": "PASS", "title": "Global File Seal Validated", "desc": "The file hash mathematically matches the document's content. Zero bytes have been altered.", "math": f"Seal Hash: {expected_seal[:20]}..."})

        last_ledger_hash = "0" * 64
        for idx, block in enumerate(data.get('metadata_ledger', [])):
            if not constant_time_compare(block['previous_hash'], last_ledger_hash):
                return False, audit_trail, f"TAMPER: Ledger Chain broken at block {idx}!"
            calc_block = {k:v for k,v in block.items() if k != 'block_hash'}
            calc_hash = hashlib.sha256(json.dumps(calc_block, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
            if not constant_time_compare(calc_hash, block['block_hash']):
                return False, audit_trail, f"TAMPER: Ledger Block {idx} hash invalid!"
            last_ledger_hash = calc_hash
        audit_trail.append({"step": 2, "status": "PASS", "title": "Blockchain Note Ledger Verified", "desc": f"All {len(data.get('metadata_ledger', []))} historical notes are chronologically intact."})

        c = data['cryptography']
        if not constant_time_compare(hash_server_seed(c['server_seed_revealed']), c['server_seed_hash']):
            return False, audit_trail, "CRITICAL: Server seed hash does not match revealed seed!"
        audit_trail.append({"step": 3, "status": "PASS", "title": "Cryptographic Pre-Commitment Validated", "desc": "The server correctly locked its randomness before seeing the participants list.", "math": f"SHA256 Seed Proof: {c['server_seed_hash'][:20]}..."})

        last_hash = "0" * 64
        for i, entry in enumerate(data['execution_log']):
            if not constant_time_compare(entry['previous_hash'], last_hash): return False, audit_trail, "TAMPER: Execution chain broken."
            calc_hash = hashlib.sha256((last_hash + json.dumps(entry['event'], sort_keys=True, separators=(',', ':'))).encode()).hexdigest()
            if not constant_time_compare(calc_hash, entry['current_hash']): return False, audit_trail, "TAMPER: Execution event modified."
            last_hash = calc_hash
            
        mode = data['mode']
        arr = data['input_list'].copy()
        raw_entropy = c['raw_entropy']
        revealed_seed = c['server_seed_revealed']
        client_seed = c['client_seed']

        if mode == "weighted_shuffle":
            results = []
            nonce = 0
            for item in arr:
                w = float(item['weight']) + 1.0
                derived = generate_hmac_entropy(revealed_seed, client_seed, nonce, raw_entropy)
                u = int(derived, 16) / ((1 << 256) - 1)
                if u == 0: u = 1e-10
                score = u ** (1.0 / w)
                results.append({"name": item['name'], "score": score})
                nonce += 1
            results.sort(key=lambda x: x['score'])
            expected_order = [r['name'] for r in results]
            if expected_order != data['result']: return False, audit_trail, "WEIGHTED SHUFFLE MISMATCH."
            math_proof = f"Calculated {nonce} deterministic floating-point scores using A-Res Alg: U^(1/W)."

        elif mode in ["lottery", "pop_quiz_1", "raffle"]:
            derived = generate_hmac_entropy(revealed_seed, client_seed, 0, raw_entropy)
            winner_idx, large_int = map_entropy_to_index(derived, len(arr))
            if data['result'][0] != arr[winner_idx]: return False, audit_trail, "RESULT MISMATCH."
            math_proof = f"Int: {str(large_int)[:15]}... Modulo {len(arr)} = Index {winner_idx}"
        else:
            nonce = 0
            for i in range(len(arr) - 1, 0, -1):
                derived = generate_hmac_entropy(revealed_seed, client_seed, nonce, raw_entropy)
                j, large_int = map_entropy_to_index(derived, i + 1)
                arr[i], arr[j] = arr[j], arr[i]
                nonce += 1
            
            params = data.get('mode_params', {})
            math_proof = f"Recomputed {nonce} perfect deterministic shuffle swaps using Fisher-Yates."
            
            if mode == "sequential" and arr != data['result']: return False, audit_trail, "SHUFFLE MISMATCH."
            elif mode in ["multi_lottery", "captains", "pop_quiz_n"] and arr[:params.get('count', 2)] != data['result']: return False, audit_trail, "MULTI-WINNER MISMATCH."
            elif mode == "teams" and chunk_into_teams(arr, params.get('num_teams', 2)) != data['result']: return False, audit_trail, "TEAM MISMATCH."
            elif mode == "pairs" and chunk_into_pairs(arr) != data['result']: return False, audit_trail, "PAIRS MISMATCH."
            elif mode == "roles" and apply_roles(arr, params.get('roles', '')) != data['result']: return False, audit_trail, "ROLES MISMATCH."
            elif mode == "secret_santa" and apply_secret_santa(arr) != data['result']: return False, audit_trail, "SANTA MISMATCH."
            elif mode == "bracket" and generate_bracket(arr) != data['result']: return False, audit_trail, "BRACKET MISMATCH."
            elif mode == "seating":
                if 'table_rows' in params: # New 3-Tier Check
                    if chunk_into_classroom(arr, params['table_rows'], params['table_cols'], params['seats_per_table']) != data['result']: return False, audit_trail, "SEATING MISMATCH."
                elif 'cols' in params: # Legacy check 1
                    if chunk_into_rows_cols(arr, params['cols'], params['rows']) != data['result']: return False, audit_trail, "SEATING MISMATCH."
                else: # Legacy check 2
                    if chunk_into_tables(arr, params.get('tables', 6), params.get('seats_per_table', 4)) != data['result']: return False, audit_trail, "SEATING MISMATCH."

        audit_trail.append({"step": 4, "status": "PASS", "title": "Mathematical Execution Reproduced", "desc": "All HMAC hashes were recalculated. Modulo/Float arithmetic perfectly reproduces the final selection.", "math": math_proof})

        if 'signature' in data:
            if input_password:
                expected_sig = compute_signature(data, input_password)
                if constant_time_compare(expected_sig, data['signature']['signature_hash']):
                    audit_trail.append({"step": 5, "status": "PASS", "title": "Teacher Signature Confirmed", "desc": f"The password proved {data['signature']['signer_name']} authorized this exact file."})
                else:
                    audit_trail.append({"step": 5, "status": "FAIL", "title": "Password Verification Failed", "desc": "The mathematical operations are valid, but the teacher's password was incorrect."})
                    return False, audit_trail, "File intact, but SIGNATURE PASSWORD INCORRECT."
            else:
                audit_trail.append({"step": 5, "status": "WARN", "title": "Signature Unverified", "desc": f"The file is signed by {data['signature']['signer_name']}, but you did not provide the password to verify the authority claim."})

        return True, audit_trail, "VERIFIED SUCCESS: Result is mathematically flawless and untampered."
        
    except Exception as e:
        audit_trail.append({"step": 0, "status": "FAIL", "title": "Malformed Document", "desc": f"The audit could not run. Error: {str(e)}"})
        return False, audit_trail, "VERIFICATION FAILED: Malformed file."