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
    # Speed features (he has these, we want to remove them)
    'RunSpeed', 'DashSpeedScale', 'CrouchSpeed', 'CreepSpeed',
    'DieingSpeed', 'StropSpeed', 'HorseSpeedLineSpeed', 'HorseDeadSpeed',
    'SpeedMultiplier', 'RunSpeedMultiplier',
    
    # Jump features
    'MaxJumpHeight', 'JumpHeightMultiplier',
    'SkyDivingSpeedDelta', 'SkyDivingRotationSpeed', 'SkySurfingSpeedDelta',
    'ParachutingMaxAngleTilt', 'ParachutingMinAngleTilt',
    
    # Back jump
    'EnableBackJump', 'BackJumpSpeed',
    
    # High sensitivity
    'SensitivityMaxSetting', 'Sensitivity1PMaxSetting',
    'X1ScopeMaxSetting', 'X2ScopeMaxSetting', 'X4ScopeMaxSetting',
    'X8ScopeMaxSetting', 'FreeLookMaxSetting',
    
    # Other unwanted
    'EnableAccelerationOnFalling', 'CanJumpFallingRunFast',
    'CanCreepRunFast', 'CanCrouchingRunFast', 'StropFallingResetSpeed',
    'ShowHighFrameRateSetting', 'Real60FrameSwitch', 'HighFPSSetting',
]

# ============================================================
# FEATURES TO ADD (These are NOT in his config)
# ============================================================
FEATURES_TO_ADD = [
    # ----- HEADSHOT (Missing from his config) -----
    'HeadShotOnly,HeadShotOnly,bool,true,,',
    'HeadShotMultiplier,HeadShotMultiplier,float,999.0,,',
    'HeadShotDamageScale,HeadShotDamageScale,float,999.0,,',
    'EnableHeadShotHitEffect,EnableHeadShotHitEffect,bool,true,,',
    'HeadshotSightFXOpen,HeadshotSightFXOpen,bool,true,,',
    
    # ----- DAMAGE (Missing from his config) -----
    'DamageMultiplier,DamageMultiplier,float,999.0,,',
    'DamageRatioHead,DamageRatioHead,float,999.0,,',
    'MaxDamage,MaxDamage,int,999,,',
    
    # ----- NO RECOIL (Missing from his config) -----
    'FPPRecoil,FPPRecoil,bool,false,,',
    'FPPRecoilYFactor,FPPRecoilYFactor,float,0.0,,',
    'FPPRecoilZFactor,FPPRecoilZFactor,float,0.0,,',
    'RecoilYCycle,RecoilYCycle,float,0.0,,',
    'RecoilZCycle,RecoilZCycle,float,0.0,,',
    'RecoilBackwardX,RecoilBackwardX,float,0.0,,',
    'RecoilBackwardZ,RecoilBackwardZ,float,0.0,,',
]

# ============================================================
# NUKE FUNCTION - Remove unwanted, add missing features
# ============================================================
def nuke_and_add(gamevar):
    """Remove unwanted features and add missing ones"""
    
    if not gamevar:
        return gamevar
    
    lines = gamevar.split('\n')
    cleaned_lines = []
    
    # Remove unwanted features
    for line in lines:
        should_keep = True
        for unwanted in UNWANTED_FEATURES:
            if line.startswith(unwanted + ',') or line.startswith(unwanted + ':'):
                should_keep = False
                logging.info(f"Removed: {line[:50]}...")
                break
        
        if should_keep:
            cleaned_lines.append(line)
    
    # Add missing features (headshot, damage, no recoil)
    cleaned_lines.extend(FEATURES_TO_ADD)
    logging.info(f"Added missing features (Headshot, Damage, No Recoil)")
    
    return '\n'.join(cleaned_lines)

# ============================================================
# PROXY ENDPOINT
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
        response = requests.get(HIS_CONFIG_URL, params=params, headers=headers, timeout=10)
        logging.info(f"His server response: {response.status_code}")
        
        if response.status_code == 200:
            try:
                his_config = response.json()
                logging.info("Got his config")
                
                if 'gamevar' in his_config:
                    original_len = len(his_config['gamevar'])
                    his_config['gamevar'] = nuke_and_add(his_config['gamevar'])
                    new_len = len(his_config['gamevar'])
                    logging.info(f"Gamevar modified: {original_len} -> {new_len} bytes")
                
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
        .features li { padding: 4px 0; }
        .removed { color: #ff6b6b; }
        .added { color: #4fc3f7; }
        .kept { color: #aaa; }
    </style>
    </head>
    <body>
    <div class="status">🟢 Proxy Active</div>
    <div class="info">Nuking unwanted, adding missing features</div>
    <div class="features">
        <h3 style="color:#fff;">Status:</h3>
        <ul style="list-style:none;padding:0;">
            <li class="removed">❌ Speed, Jump, Back Jump, High Sensitivity</li>
            <li class="removed">❌ Rapid Fire (REMOVED)</li>
            <li class="added">✅ Headshot (HeadShotOnly, HeadShotMultiplier)</li>
            <li class="added">✅ Damage (DamageMultiplier, DamageRatioHead)</li>
            <li class="added">✅ No Recoil (FPPRecoil, FPPRecoilYFactor)</li>
            <li class="kept">✅ Everything else from his config preserved</li>
        </ul>
        <p style="color:#444;font-size:12px;margin-top:20px;">
            Missing features from dump.cs added | Unwanted features nuked
        </p>
    </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
