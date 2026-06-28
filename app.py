from flask import Flask, request, Response, jsonify
import requests
import json
import logging
import urllib.parse

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# ============================================================
# REAL GARENA CONFIG SERVER
# ============================================================
GARENA_BASE = "https://gin.freefiremobile.com"

# ============================================================
# USER PREFERENCES (Save in memory)
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

# ============================================================
# INJECT FEATURES INTO GAMEVAR
# ============================================================
def inject_features(gamevar):
    """Inject mod features into the gamevar string"""
    
    features = []
    
    # Headshot features
    if user_prefs.get('HS_NECK') or user_prefs.get('HS_CHEST'):
        features.append("EnableHeadshotOnly,EnableHeadshotOnly,bool,true,,")
        features.append("HeadshotMultiplier,HeadshotMultiplier,float,999.0,,")
        features.append("OneShotKill,OneShotKill,bool,true,,")
        features.append("DamageMultiplier,DamageMultiplier,float,999.0,,")
    
    # Speed hack
    if user_prefs.get('SPEED_HACK'):
        features.append("SpeedMultiplier,SpeedMultiplier,float,2.0,,")
        features.append("RunSpeedMultiplier,RunSpeedMultiplier,float,2.0,,")
    
    # High jump
    if user_prefs.get('HIGH_JUMP'):
        features.append("MaxJumpHeight,MaxJumpHeight,float,999,,")
        features.append("JumpHeightMultiplier,JumpHeightMultiplier,float,5.0,,")
    
    # Rapid fire
    if user_prefs.get('RAPID_FIRE'):
        features.append("FireRateMultiplier,FireRateMultiplier,float,2.0,,")
        features.append("OneShotLimitInOneFrame,OneShotLimitInOneFrame,int,999,,")
    
    # No cooldown
    if user_prefs.get('NO_CD_MICS'):
        features.append("UseMedkitTime,UseMedkitTime,float,0.1,,")
        features.append("UseArmortoolsTime,UseArmortoolsTime,float,0.1,,")
        features.append("ReviveTimeout,ReviveTimeout,int,1,,")
        features.append("StropUseCooldown,StropUseCooldown,float,0,,")
        features.append("SwitchStropCD,SwitchStropCD,float,0,,")
        features.append("StropBoostCooldown,StropBoostCooldown,float,0,,")
    
    # No swap (instant weapon swap)
    if user_prefs.get('NO_SWAP'):
        features.append("SwapWeaponCD,SwapWeaponCD,float,0,,")
        features.append("SwitchWeaponInterval,SwitchWeaponInterval,float,0,,")
        features.append("ReloadTimeMultiplier,ReloadTimeMultiplier,float,0.1,,")
    
    # High sensitivity
    if user_prefs.get('HIGH_SENSI'):
        features.append("SensitivityMaxSetting,SensitivityMaxSetting,float,999.0,,")
        features.append("Sensitivity1PMaxSetting,Sensitivity1PMaxSetting,float,999.0,,")
        features.append("X1ScopeMaxSetting,X1ScopeMaxSetting,float,999.0,,")
        features.append("X2ScopeMaxSetting,X2ScopeMaxSetting,float,999.0,,")
        features.append("X4ScopeMaxSetting,X4ScopeMaxSetting,float,999.0,,")
        features.append("X8ScopeMaxSetting,X8ScopeMaxSetting,float,999.0,,")
        features.append("FreeLookMaxSetting,FreeLookMaxSetting,float,999.0,,")
    
    # Bypass (anti-ban)
    if user_prefs.get('BYPASSV1'):
        features.append("CheckHacker,CheckHacker,bool,false,,")
        features.append("DebugHack,DebugHack,bool,true,,")
        features.append("TestModeEnabled,TestModeEnabled,bool,true,,")
        features.append("DisableGinInfoSend,DisableGinInfoSend,int,1,,")
        features.append("CleanFFAntiState,CleanFFAntiState,bool,true,,")
    
    if features:
        gamevar += "\n" + "\n".join(features) + ","
    
    return gamevar

# ============================================================
# PROXY ENDPOINT - Forwards to Garena and modifies response
# ============================================================
@app.route('/ver.php', methods=['GET', 'POST'])
def proxy_ver_php():
    """Forward request to Garena, modify response"""
    
    logging.info(f"Request from: {request.remote_addr}")
    logging.info(f"Query params: {dict(request.args)}")
    
    # ============================================================
    # STEP 1: Build the request to Garena
    # ============================================================
    url = f"{GARENA_BASE}/ver.php"
    
    # Forward all query parameters
    params = request.args.to_dict()
    
    # Forward headers (important ones)
    headers = {
        'User-Agent': request.headers.get('User-Agent', 'UnityPlayer/2022.3.47f1'),
        'Accept': request.headers.get('Accept', '*/*'),
        'Accept-Encoding': request.headers.get('Accept-Encoding', 'gzip, deflate, br'),
        'Connection': request.headers.get('Connection', 'keep-alive'),
    }
    
    # ============================================================
    # STEP 2: Forward request to Garena
    # ============================================================
    try:
        logging.info(f"Forwarding to: {url}")
        garena_response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=15
        )
        
        logging.info(f"Garena response status: {garena_response.status_code}")
        
        # ============================================================
        # STEP 3: Parse and modify the response
        # ============================================================
        if garena_response.status_code == 200:
            try:
                config = garena_response.json()
                logging.info(f"Got config from Garena, length: {len(str(config))}")
                
                # Inject features
                if 'gamevar' in config:
                    config['gamevar'] = inject_features(config['gamevar'])
                    logging.info("Injected features into gamevar")
                
                # Return modified config
                json_str = json.dumps(config, separators=(',', ':'), ensure_ascii=False)
                logging.info(f"Modified response length: {len(json_str)} bytes")
                
                response = Response(
                    json_str,
                    status=200,
                    mimetype='application/json'
                )
                response.headers['Content-Type'] = 'application/json'
                response.headers['Access-Control-Allow-Origin'] = '*'
                response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Expires'] = '0'
                
                return response
                
            except json.JSONDecodeError:
                logging.error("Failed to parse Garena response as JSON")
                # Return raw response
                return garena_response.text, garena_response.status_code
        
        # If Garena returned error, forward it
        return garena_response.text, garena_response.status_code
        
    except requests.exceptions.Timeout:
        logging.error("Timeout connecting to Garena")
        return jsonify({"code": 2, "message": "proxy timeout"}), 504
    except Exception as e:
        logging.error(f"Error: {e}")
        return jsonify({"code": 2, "message": "proxy error"}), 500

# ============================================================
# API CONFIG - Toggle preferences
# ============================================================
@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    if request.method == 'POST':
        data = request.json
        for key in data:
            if key in user_prefs:
                user_prefs[key] = data[key]
        logging.info(f"Updated prefs: {user_prefs}")
        return jsonify({"status": "ok", "prefs": user_prefs})
    else:
        return jsonify(user_prefs)

# ============================================================
# HEALTH CHECK
# ============================================================
@app.route('/health')
def health():
    return jsonify({"status": "ok", "message": "Proxy server running"})

# ============================================================
# WEB UI
# ============================================================
@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>Proxy Control Panel</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: #0a0a0f; color: #fff; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 20px; min-height: 100vh; }
        .container { max-width: 500px; margin: auto; }
        h1 { text-align: center; font-size: 28px; font-weight: 700; margin: 20px 0 5px; background: linear-gradient(135deg, #4fc3f7, #7c4dff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .subtitle { text-align: center; color: #888; font-size: 14px; margin-bottom: 20px; }
        .status { text-align: center; padding: 12px; background: rgba(79, 195, 247, 0.1); border-radius: 10px; margin-bottom: 20px; color: #4fc3f7; font-size: 14px; border: 1px solid rgba(79, 195, 247, 0.2); }
        .status i { margin-right: 8px; }
        .toggle-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        .toggle-item { background: #15151f; padding: 15px; border-radius: 12px; cursor: pointer; border: 1px solid #2a2a3a; transition: all 0.3s; }
        .toggle-item:hover { border-color: #4fc3f7; }
        .toggle-item.active { border-color: #4fc3f7; background: rgba(79, 195, 247, 0.05); }
        .toggle-item.important.active { border-color: #ff6b6b; background: rgba(255, 107, 107, 0.05); }
        .toggle-item .label { font-size: 13px; font-weight: 600; display: flex; align-items: center; justify-content: space-between; }
        .toggle-item .label i { color: #4fc3f7; width: 18px; }
        .toggle-item.important .label i { color: #ff6b6b; }
        .toggle-item .description { font-size: 10px; color: #666; margin-top: 4px; padding-left: 26px; }
        .toggle-switch { width: 36px; height: 20px; background: #2a2a3a; border-radius: 10px; position: relative; transition: 0.3s; flex-shrink: 0; }
        .toggle-switch::after { content: ''; position: absolute; width: 16px; height: 16px; background: #555; border-radius: 50%; top: 2px; left: 2px; transition: 0.3s; }
        .toggle-item.active .toggle-switch { background: #4fc3f7; }
        .toggle-item.active .toggle-switch::after { left: 18px; background: #fff; }
        .toggle-item.important.active .toggle-switch { background: #ff6b6b; }
        .footer { text-align: center; margin-top: 20px; color: #444; font-size: 11px; }
        .footer i { margin: 0 4px; }
        .toast { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background: #1a1a2e; padding: 12px 24px; border-radius: 10px; border: 1px solid #4fc3f7; display: none; }
        @media (max-width: 400px) { .toggle-grid { grid-template-columns: 1fr; } }
    </style>
    </head>
    <body>
    <div class="container">
        <h1><i class="fas fa-bolt"></i> PROXY</h1>
        <p class="subtitle">Game Modification Proxy</p>
        <div class="status"><i class="fas fa-circle" style="color:#4fc3f7;font-size:10px;"></i> Proxy Active</div>
        <div class="toggle-grid" id="toggleGrid"></div>
        <div class="footer"><i class="fas fa-sync-alt"></i> Restart game after changing settings</div>
    </div>
    <div class="toast" id="toast">✅ Settings saved</div>
    <script>
        const toggles = {
            HS_NECK: { label: 'HS NECK', desc: 'Neck shots = headshot', icon: 'fa-crosshairs' },
            HS_CHEST: { label: 'HS CHEST', desc: 'Chest shots = headshot', icon: 'fa-crosshairs' },
            SPEED_HACK: { label: 'SPEED HACK', desc: '2x movement speed', icon: 'fa-bolt' },
            BACKJUMPV1: { label: 'BACK JUMP', desc: 'Old back jump mechanic', icon: 'fa-arrow-up' },
            NO_SWAP: { label: 'NO SWAP', desc: 'Instant weapon swap', icon: 'fa-exchange-alt' },
            BYPASSV1: { label: 'BYPASS', desc: 'Anti-ban protection', icon: 'fa-shield-alt', important: true },
            HIGH_JUMP: { label: 'HIGH JUMP', desc: 'Increased jump height', icon: 'fa-arrow-up' },
            NO_CD_MICS: { label: 'NO CD MICS', desc: 'No cooldown + fast landing', icon: 'fa-clock' },
            RAPID_FIRE: { label: 'RAPID FIRE', desc: 'Increased fire rate', icon: 'fa-fire' },
            HIGH_FPS: { label: 'HIGH FPS', desc: 'Frame rate boost', icon: 'fa-video' },
            HIGH_SENSI: { label: 'HIGH SENSI', desc: 'Sensitivity set to 999', icon: 'fa-sliders-h' }
        };
        
        async function loadConfig() {
            try {
                const resp = await fetch('/api/config');
                const config = await resp.json();
                const grid = document.getElementById('toggleGrid');
                grid.innerHTML = '';
                for (const [key, data] of Object.entries(toggles)) {
                    const div = document.createElement('div');
                    div.className = 'toggle-item' + (config[key] ? ' active' : '') + (data.important ? ' important' : '');
                    div.innerHTML = `
                        <div class="label">
                            <span><i class="fas ${data.icon}"></i> ${data.label}</span>
                            <div class="toggle-switch"></div>
                        </div>
                        <div class="description">${data.desc}</div>
                    `;
                    div.onclick = async () => {
                        div.classList.toggle('active');
                        const newState = div.classList.contains('active');
                        config[key] = newState;
                        await fetch('/api/config', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(config) });
                        showToast('✅ Settings saved');
                    };
                    grid.appendChild(div);
                }
            } catch(e) { console.error('Error loading config:', e); }
        }
        
        function showToast(msg) {
            const toast = document.getElementById('toast');
            toast.textContent = msg;
            toast.style.display = 'block';
            setTimeout(() => { toast.style.display = 'none'; }, 2000);
        }
        
        loadConfig();
    </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
