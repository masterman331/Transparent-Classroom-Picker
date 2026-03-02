import os
import uuid
import json
import datetime
from flask import Flask, render_template, request, redirect, url_for, session, send_file
from config import Config
import crypto_engine
import random_engine
import shuffle_engine
import verify_engine
from log_engine import create_ledger_block

app = Flask(__name__)
app.config.from_object(Config)

RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')
os.makedirs(RESULTS_DIR, exist_ok=True)

MODES = {
    'sequential': 'Sequential Order (Randomize Full List)',
    'lottery': 'Single Winner (Draw 1 Name)',
    'multi_lottery': 'Multi-Winner (Draw N Names)',
    'teams': 'Team Generator (Divide into N Teams)',
    'pairs': 'Pairs Generator (Groups of 2)',
    'roles': 'Role Assignment (Assign specific jobs)',
    'secret_santa': 'Secret Santa (Perfect derangement circle)',
    'captains': 'Select Team Captains (Draw N)',
    'pop_quiz_1': 'Pop Quiz Victim (Draw 1)',
    'pop_quiz_n': 'Pop Quiz Group (Draw N)',
    'raffle': 'Weighted Raffle Draw (Name:Tickets)',
    'weighted_shuffle': 'Weighted Queue Shuffle (Name:DelayPriority)',
    'bracket': 'Tournament Bracket (1v1 Matchups)',
    'seating': 'Classroom Seating Chart (Tables & Seats)'
}

@app.route('/')
def index():
    return render_template('index.html', modes=MODES)

@app.route('/history')
def history():
    files_data = []
    for filename in os.listdir(RESULTS_DIR):
        if filename.endswith('.json'):
            try:
                with open(os.path.join(RESULTS_DIR, filename), 'r', encoding='utf-8') as f: 
                    data = json.load(f)
                latest_ledger = data['metadata_ledger'][-1] if data.get('metadata_ledger') else {}
                files_data.append({
                    "id": data['file_id'], "date": data['generation_time'], "mode": data['mode'],
                    "title": latest_ledger.get('title', 'Untitled'), "notes": latest_ledger.get('notes', ''),
                    "signer": data.get('signature', {}).get('signer_name', 'None')
                })
            except Exception: pass
    files_data.sort(key=lambda x: x['date'], reverse=True)
    return render_template('history.html', history=files_data)

@app.route('/input/<mode>')
def input_page(mode):
    if mode not in MODES: return redirect(url_for('index'))
    server_seed = crypto_engine.generate_server_seed()
    session['server_seed'] = server_seed
    return render_template(
        'input.html', mode=mode, mode_name=MODES[mode], 
        ss_hash=crypto_engine.hash_server_seed(server_seed), client_seed=random_engine.generate_client_seed()
    )

@app.route('/process', methods=['POST'])
def process():
    mode = request.form.get('mode')
    raw_names_input = request.form.get('names', '')
    client_seed = request.form.get('client_seed') or random_engine.generate_client_seed()
    entropy_source = request.form.get('entropy_source')
    signer_name = request.form.get('signer_name', '').strip()
    signer_pass = request.form.get('signer_pass', '').strip()
    
    # Capture Animation Timing Preferences
    session['dramatic_mode'] = request.form.get('dramatic_mode', '0')
    session['dramatic_time'] = request.form.get('dramatic_time', '15') # Default 15 seconds
    
    server_seed = session.get('server_seed')
    if not server_seed: return "Session expired.", 400
    
    names = []
    if mode == 'raffle':
        for n in raw_names_input.split('\n'):
            if not n.strip(): continue
            parts = n.split(':')
            name = parts[0].strip()
            tickets = int(parts[1].strip()) if len(parts) > 1 and parts[1].strip().isdigit() else 1
            names.extend([name] * tickets)
    elif mode == 'weighted_shuffle':
        for n in raw_names_input.split('\n'):
            if not n.strip(): continue
            parts = n.split(':')
            name = parts[0].strip()
            try: weight = float(parts[1].strip()) if len(parts) > 1 else 0.0
            except ValueError: weight = 0.0
            names.append({"name": name, "weight": weight})
    else:
        names = [n.strip() for n in raw_names_input.split('\n') if n.strip()][:Config.MAX_ENTRIES]
        
    if len(names) < 2: return "At least 2 names/tickets required.", 400
    
    raw_entropy, entropy_meta = random_engine.get_entropy(entropy_source)
    mode_params = {}

    if mode in ['lottery', 'pop_quiz_1', 'raffle']:
        result, log_chain = shuffle_engine.process_lottery(names, server_seed, client_seed, raw_entropy)
    elif mode == 'weighted_shuffle':
        result, log_chain = shuffle_engine.process_weighted_shuffle(names, server_seed, client_seed, raw_entropy)
    else:
        shuffled_arr, log_chain = shuffle_engine.process_shuffle(names, server_seed, client_seed, raw_entropy)
        if mode == 'sequential': result = shuffled_arr
        elif mode in ['multi_lottery', 'captains', 'pop_quiz_n']:
            count = int(request.form.get('num_count', 2))
            mode_params['count'] = count
            result = shuffled_arr[:count]
        elif mode == 'teams':
            num_teams = int(request.form.get('num_teams', 2))
            mode_params['num_teams'] = num_teams
            result = shuffle_engine.chunk_into_teams(shuffled_arr, num_teams)
        elif mode == 'pairs': result = shuffle_engine.chunk_into_pairs(shuffled_arr)
        elif mode == 'roles':
            roles_str = request.form.get('roles_list', '')
            mode_params['roles'] = roles_str
            result = shuffle_engine.apply_roles(shuffled_arr, roles_str)
        elif mode == 'secret_santa': result = shuffle_engine.apply_secret_santa(shuffled_arr)
        elif mode == 'seating':
            t_rows = int(request.form.get('table_rows', 3))
            t_cols = int(request.form.get('table_cols', 2))
            seats = int(request.form.get('seats_per_table', 4))
            mode_params['table_rows'], mode_params['table_cols'], mode_params['seats_per_table'] = t_rows, t_cols, seats
            result = shuffle_engine.chunk_into_classroom(shuffled_arr, t_rows, t_cols, seats)
        elif mode == 'bracket': result = shuffle_engine.generate_bracket(shuffled_arr)

    file_id = str(uuid.uuid4())
    output_data = {
        "file_id": file_id, "generation_time": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "mode": mode, "mode_params": mode_params, "input_list": names, "result": result,
        "cryptography": {
            "server_seed_hash": crypto_engine.hash_server_seed(server_seed),
            "server_seed_revealed": server_seed, "client_seed": client_seed,
            "entropy_source": entropy_source, "raw_entropy": raw_entropy, "entropy_metadata": entropy_meta
        },
        "execution_log": log_chain.export()
    }

    custom_title = request.form.get('custom_title', f"Selection: {mode}")
    output_data['metadata_ledger'] = [create_ledger_block(custom_title, "Original Generation.", "System", "0"*64)]

    if not signer_name: 
        signer_name, signer_pass = "System Auto-Signer", random_engine.secrets.token_hex(4)
        session['last_auto_pass'] = signer_pass
    output_data['signature'] = {"signer_name": signer_name, "signature_hash": crypto_engine.compute_signature(output_data, signer_pass)}
    output_data['final_file_seal'] = crypto_engine.compute_file_seal(output_data)

    with open(os.path.join(RESULTS_DIR, f"{file_id}.json"), 'w', encoding='utf-8') as f: json.dump(output_data, f, indent=4)
    return redirect(url_for('result', file_id=file_id))

@app.route('/result/<file_id>')
def result(file_id):
    path = os.path.join(RESULTS_DIR, f"{file_id}.json")
    if not os.path.exists(path): return "Not found", 404
    with open(path, 'r', encoding='utf-8') as f: data = json.load(f)
    
    dramatic_mode = session.pop('dramatic_mode', '0')
    dramatic_time = session.pop('dramatic_time', '15')
    return render_template('result.html', data=data, file_id=file_id, dramatic_mode=dramatic_mode, dramatic_time=dramatic_time, auto_pass=session.pop('last_auto_pass', None))

@app.route('/append_note/<file_id>', methods=['POST'])
def append_note(file_id):
    path = os.path.join(RESULTS_DIR, f"{file_id}.json")
    with open(path, 'r', encoding='utf-8') as f: data = json.load(f)
    
    pwd = request.form.get('edit_password', '')
    if 'signature' in data and data['signature']['signature_hash'] != crypto_engine.compute_signature(data, pwd):
        return "ERROR: Incorrect Signature Password.", 403

    last_hash = data['metadata_ledger'][-1]['block_hash']
    new_block = create_ledger_block(request.form.get('title'), request.form.get('notes'), request.form.get('author'), last_hash)
    data['metadata_ledger'].append(new_block)
    
    data['signature']['signature_hash'] = crypto_engine.compute_signature(data, pwd)
    data['final_file_seal'] = crypto_engine.compute_file_seal(data)

    with open(path, 'w', encoding='utf-8') as f: json.dump(data, f, indent=4)
    return redirect(url_for('result', file_id=file_id))

@app.route('/download/<file_id>')
def download(file_id):
    return send_file(os.path.join(RESULTS_DIR, f"{file_id}.json"), as_attachment=True, download_name=f"Class_Audit_{file_id}.json")

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        file, pwd = request.files.get('file'), request.form.get('verify_pass', '')
        if not file: return "No file", 400
        try:
            is_valid, log, msg = verify_engine.verify_file_data(json.loads(file.read().decode('utf-8')), pwd)
            return render_template('verify.html', message=msg, is_valid=is_valid, audit_trail=log)
        except Exception as e:
            return render_template('verify.html', message=f"Error: {e}", is_valid=False, audit_trail=[])
    return render_template('verify.html')

if __name__ == '__main__': 
    app.run(port=Config.PORT, debug=Config.DEBUG, use_reloader=False)