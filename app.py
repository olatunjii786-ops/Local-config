from flask import Flask, request, Response, jsonify
import requests
import json
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

HIS_CONFIG_URL = "https://niku-mods-proxy-1.onrender.com/ver.php"

# ============================================================
# FEATURES TO REMOVE (Nuke these from his config)
# ============================================================
UNWANTED_FEATURES = [
    # Speed features
    'RunSpeed',
    'DashSpeedScale', 
    'CrouchSpeed',
    'CreepSpeed',
    'DieingSpeed',
    'StropSpeed',
    'HorseSpeedLineSpeed',
    'HorseDeadSpeed',
    'SpeedMultiplier',
    'RunSpeedMultiplier',
    
    # Jump features
    'MaxJumpHeight',
    'JumpHeightMultiplier',
    'SkyDivingSpeedDelta',
    'SkyDivingRotationSpeed',
    'SkySurfingSpeedDelta',
    'ParachutingMaxAngleTilt',
    'ParachutingMinAngleTilt',
    
    # Back jump
    'EnableBackJump',
    'BackJumpSpeed',
    
    # High sensitivity
    'SensitivityMaxSetting',
    'Sensitivity1PMaxSetting',
    'X1ScopeMaxSetting',
    'X2ScopeMaxSetting',
    'X4ScopeMaxSetting',
    'X8ScopeMaxSetting',
    'FreeLookMaxSetting',
    
    # Other unwanted
    'EnableAccelerationOnFalling',
    'CanJumpFallingRunFast',
    'CanCreepRunFast',
    'CanCrouchingRunFast',
    'StropFallingResetSpeed',
]

# ============================================================
# NUKE FUNCTION - Remove unwanted lines from gamevar
# ============================================================
def nuke_unwanted_features(gamevar):
    """Remove all unwanted feature lines from gamevar"""
    
    if not gamevar:
        return gamevar
    
    lines = gamevar.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Check if this line contains any unwanted feature
        should_keep = True
        for unwanted in UNWANTED_FEATURES:
            if line.startswith(unwanted + ',') or line.startswith(unwanted + ':'):
                should_keep = False
                logging.info(f"Removed: {line[:50]}...")
                break
        
        if should_keep:
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

# ============================================================
# PROXY ENDPOINT - Get his config, nuke unwanted, pass rest
# ============================================================
@app.route('/ver.php', methods=['GET', 'POST'])
def proxy_ver_php():
    logging.info(f"Request from: {request.remote_addr}")
    
    params = request.args.to_dict()
    headers = {
        'User-Agent': request.headers.get('User-Agent', 'UnityPlayer/2022.3.47f1'),
        'Accept': request.headers.get('Accept', '*/*'),
        'Connection': 'keep-alive',
    }
    
    try:
        # 1. Fetch from his server
        response = requests.get(HIS_CONFIG_URL, params=params, headers=headers, timeout=10)
        logging.info(f"His server response: {response.status_code}")
        
        if response.status_code == 200:
            try:
                his_config = response.json()
                logging.info("Got his config")
                
                # 2. Nuke unwanted features from gamevar
                if 'gamevar' in his_config:
                    original_len = len(his_config['gamevar'])
                    his_config['gamevar'] = nuke_unwanted_features(his_config['gamevar'])
                    new_len = len(his_config['gamevar'])
                    logging.info(f"Gamevar nuked: {original_len} -> {new_len} bytes")
                
                # 3. Return the nuked config
                json_str = json.dumps(his_config, separators=(',', ':'), ensure_ascii=False)
                
                resp = Response(json_str, status=200, mimetype='application/json')
                resp.headers['Content-Type'] = 'application/json'
                resp.headers['Access-Control-Allow-Origin'] = '*'
                resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                resp.headers['Pragma'] = 'no-cache'
                resp.headers['Expires'] = '0'
                
                return resp
                
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse JSON: {e}")
                return response.text, response.status_code
        
        return response.text, response.status_code
        
    except Exception as e:
        logging.error(f"Error: {e}")
        return jsonify({"code": 2, "message": "proxy error"}), 500

# ============================================================
# STATUS PAGE
# ============================================================
@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>Proxy Active</title>
    <style>
        body { background: #0a0a0f; color: #fff; font-family: sans-serif; padding: 20px; text-align: center; }
        .status { color: #4fc3f7; font-size: 24px; margin-top: 50px; }
        .info { color: #666; margin-top: 20px; }
        .features { margin-top: 30px; text-align: left; max-width: 400px; margin-left: auto; margin-right: auto; }
        .features li { color: #888; padding: 4px 0; }
        .removed { color: #ff6b6b; }
    </style>
    </head>
    <body>
    <div class="status">🟢 Proxy Active</div>
    <div class="info">Nuking unwanted features from his config</div>
    <div class="features">
        <h3 style="color:#fff;">Removed Features:</h3>
        <ul style="list-style:none;padding:0;">
            <li class="removed">❌ Speed Hack (RunSpeed, DashSpeedScale, etc.)</li>
            <li class="removed">❌ High Jump (MaxJumpHeight, JumpHeightMultiplier, etc.)</li>
            <li class="removed">❌ Back Jump (EnableBackJump, BackJumpSpeed)</li>
            <li class="removed">❌ High Sensitivity (SensitivityMaxSetting, etc.)</li>
            <li class="removed">❌ Falling/Speed Mods</li>
        </ul>
        <p style="color:#444;font-size:12px;margin-top:20px;">Everything else from his config is preserved</p>
    </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
