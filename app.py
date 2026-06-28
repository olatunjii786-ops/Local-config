from flask import Flask, request, Response, jsonify
import requests
import json
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# ============================================================
# USE HIS SERVER AS THE SOURCE (since it works)
# ============================================================
SOURCE_URL = "https://niku-mods-proxy-1.onrender.com/ver.php"

# ============================================================
# USER PREFERENCES
# ============================================================
user_prefs = {
    "HS_NECK": True,
    "HS_CHEST": True,
    "SPEED_HACK": True,
    "BACKJUMPV1": True,
    "NO_SWAP": True,
    "BYPASSV1": True,
    "HIGH_JUMP": False,
    "NO_CD_MICS": True,
    "RAPID_FIRE": False,
    "HIGH_FPS": True,
    "HIGH_SENSI": True
}

def inject_features(gamevar):
    features = []
    
    if user_prefs.get('HS_NECK') or user_prefs.get('HS_CHEST'):
        features.append("EnableHeadshotOnly,EnableHeadshotOnly,bool,true,,")
        features.append("HeadshotMultiplier,HeadshotMultiplier,float,999.0,,")
        features.append("OneShotKill,OneShotKill,bool,true,,")
        features.append("DamageMultiplier,DamageMultiplier,float,999.0,,")
    
    if user_prefs.get('SPEED_HACK'):
        features.append("SpeedMultiplier,SpeedMultiplier,float,2.0,,")
        features.append("RunSpeedMultiplier,RunSpeedMultiplier,float,2.0,,")
    
    if user_prefs.get('HIGH_JUMP'):
        features.append("MaxJumpHeight,MaxJumpHeight,float,999,,")
        features.append("JumpHeightMultiplier,JumpHeightMultiplier,float,5.0,,")
    
    if user_prefs.get('RAPID_FIRE'):
        features.append("FireRateMultiplier,FireRateMultiplier,float,2.0,,")
        features.append("OneShotLimitInOneFrame,OneShotLimitInOneFrame,int,999,,")
    
    if user_prefs.get('NO_CD_MICS'):
        features.append("UseMedkitTime,UseMedkitTime,float,0.1,,")
        features.append("UseArmortoolsTime,UseArmortoolsTime,float,0.1,,")
        features.append("ReviveTimeout,ReviveTimeout,int,1,,")
        features.append("StropUseCooldown,StropUseCooldown,float,0,,")
        features.append("SwitchStropCD,SwitchStropCD,float,0,,")
        features.append("StropBoostCooldown,StropBoostCooldown,float,0,,")
    
    if user_prefs.get('NO_SWAP'):
        features.append("SwapWeaponCD,SwapWeaponCD,float,0,,")
        features.append("SwitchWeaponInterval,SwitchWeaponInterval,float,0,,")
        features.append("ReloadTimeMultiplier,ReloadTimeMultiplier,float,0.1,,")
    
    if user_prefs.get('HIGH_SENSI'):
        features.append("SensitivityMaxSetting,SensitivityMaxSetting,float,999.0,,")
        features.append("Sensitivity1PMaxSetting,Sensitivity1PMaxSetting,float,999.0,,")
        features.append("X1ScopeMaxSetting,X1ScopeMaxSetting,float,999.0,,")
        features.append("X2ScopeMaxSetting,X2ScopeMaxSetting,float,999.0,,")
        features.append("X4ScopeMaxSetting,X4ScopeMaxSetting,float,999.0,,")
        features.append("X8ScopeMaxSetting,X8ScopeMaxSetting,float,999.0,,")
        features.append("FreeLookMaxSetting,FreeLookMaxSetting,float,999.0,,")
    
    if user_prefs.get('BYPASSV1'):
        features.append("CheckHacker,CheckHacker,bool,false,,")
        features.append("DebugHack,DebugHack,bool,true,,")
        features.append("TestModeEnabled,TestModeEnabled,bool,true,,")
        features.append("DisableGinInfoSend,DisableGinInfoSend,int,1,,")
        features.append("CleanFFAntiState,CleanFFAntiState,bool,true,,")
    
    if features:
        gamevar += "\n" + "\n".join(features) + ","
    
    return gamevar

@app.route('/ver.php', methods=['GET', 'POST'])
def proxy_ver_php():
    logging.info(f"Request from: {request.remote_addr}")
    
    # Forward query parameters
    params = request.args.to_dict()
    
    headers = {
        'User-Agent': request.headers.get('User-Agent', 'UnityPlayer/2022.3.47f1'),
        'Accept': request.headers.get('Accept', '*/*'),
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }
    
    try:
        # Fetch from his server (which still works)
        logging.info(f"Fetching from: {SOURCE_URL}")
        response = requests.get(SOURCE_URL, params=params, headers=headers, timeout=10)
        logging.info(f"Source response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                config = response.json()
                logging.info("Got config from source server")
                
                # Inject your features
                if 'gamevar' in config:
                    config['gamevar'] = inject_features(config['gamevar'])
                    logging.info("Injected features")
                
                json_str = json.dumps(config, separators=(',', ':'), ensure_ascii=False)
                
                resp = Response(
                    json_str,
                    status=200,
                    mimetype='application/json'
                )
                resp.headers['Content-Type'] = 'application/json'
                resp.headers['Access-Control-Allow-Origin'] = '*'
                resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                resp.headers['Pragma'] = 'no-cache'
                resp.headers['Expires'] = '0'
                
                return resp
                
            except json.JSONDecodeError:
                logging.error("Failed to parse JSON from source")
                return response.text, response.status_code
        
        return response.text, response.status_code
        
    except Exception as e:
        logging.error(f"Error: {e}")
        return jsonify({"code": 2, "message": "proxy error"}), 500

@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    if request.method == 'POST':
        data = request.json
        for key in data:
            if key in user_prefs:
                user_prefs[key] = data[key]
        return jsonify({"status": "ok", "prefs": user_prefs})
    else:
        return jsonify(user_prefs)

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>Proxy</title>
    <style>
        body { background: #0a0a0f; color: #fff; font-family: sans-serif; padding: 20px; text-align: center; }
        .status { color: #4fc3f7; font-size: 24px; margin-top: 50px; }
        .info { color: #666; margin-top: 20px; }
    </style>
    </head>
    <body>
    <div class="status">🟢 Proxy Active</div>
    <div class="info">Forwarding to NIKU MODS server</div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
