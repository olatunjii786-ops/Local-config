from flask import Flask, request, jsonify, Response
import requests
import json
import logging

app = Flask(__name__)

# ============================================================
# USER PREFERENCES (Saved in memory)
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
# PROXY ENDPOINT - The game connects here
# ============================================================
@app.route('/ver.php', methods=['GET', 'POST'])
def proxy_ver_php():
    """Proxy the game's request and modify the response"""
    
    # Log the request
    logging.info(f"Game request from: {request.remote_addr}")
    
    # Fetch the real config from his server (or use your own)
    try:
        response = requests.get(
            'https://niku-mods-proxy-1.onrender.com/ver.php',
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        config = response.json()
    except:
        # Fallback: use your local config
        with open('config.json', 'r') as f:
            config = json.load(f)
    
    # ============================================================
    # MODIFY THE CONFIG BASED ON USER PREFERENCES
    # ============================================================
    
    # Get the gamevar string
    gamevar = config.get('gamevar', '')
    
    # Add headshot settings
    if user_prefs.get('HS_NECK') or user_prefs.get('HS_CHEST'):
        gamevar += "\nEnableHeadshotOnly,EnableHeadshotOnly,bool,true,,\n"
        gamevar += "HeadshotMultiplier,HeadshotMultiplier,float,999.0,,\n"
        gamevar += "OneShotKill,OneShotKill,bool,true,,\n"
        gamevar += "DamageMultiplier,DamageMultiplier,float,999.0,,"
    
    # Add speed hack
    if user_prefs.get('SPEED_HACK'):
        gamevar += "\nSpeedMultiplier,SpeedMultiplier,float,2.0,,\n"
        gamevar += "RunSpeedMultiplier,RunSpeedMultiplier,float,2.0,,"
    
    # Add no swap (instant weapon swap)
    if user_prefs.get('NO_SWAP'):
        gamevar += "\nSwapWeaponCD,SwapWeaponCD,float,0,,\n"
        gamevar += "SwitchWeaponInterval,SwitchWeaponInterval,float,0,,\n"
        gamevar += "ReloadTimeMultiplier,ReloadTimeMultiplier,float,0.1,,"
    
    # Add high jump
    if user_prefs.get('HIGH_JUMP'):
        gamevar += "\nMaxJumpHeight,MaxJumpHeight,float,999,,\n"
        gamevar += "JumpHeightMultiplier,JumpHeightMultiplier,float,5.0,,"
    
    # Add rapid fire
    if user_prefs.get('RAPID_FIRE'):
        gamevar += "\nFireRateMultiplier,FireRateMultiplier,float,2.0,,\n"
        gamevar += "OneShotLimitInOneFrame,OneShotLimitInOneFrame,int,999,,"
    
    # Add high FPS
    if user_prefs.get('HIGH_FPS'):
        gamevar += "\nShowHighFrameRateSetting,ShowHighFrameRateSetting,bool,true,,\n"
        gamevar += "Real60FrameSwitch,Real60FrameSwitch,bool,true,,"
    
    # Add high sensitivity
    if user_prefs.get('HIGH_SENSI'):
        gamevar += "\nSensitivityMaxSetting,SensitivityMaxSetting,float,999.0,,\n"
        gamevar += "Sensitivity1PMaxSetting,Sensitivity1PMaxSetting,float,999.0,,\n"
        gamevar += "X1ScopeMaxSetting,X1ScopeMaxSetting,float,999.0,,\n"
        gamevar += "X2ScopeMaxSetting,X2ScopeMaxSetting,float,999.0,,\n"
        gamevar += "X4ScopeMaxSetting,X4ScopeMaxSetting,float,999.0,,\n"
        gamevar += "X8ScopeMaxSetting,X8ScopeMaxSetting,float,999.0,,\n"
        gamevar += "FreeLookMaxSetting,FreeLookMaxSetting,float,999.0,,"
    
    # Add no CD/mics
    if user_prefs.get('NO_CD_MICS'):
        gamevar += "\nUseMedkitTime,UseMedkitTime,float,0.1,,\n"
        gamevar += "UseArmortoolsTime,UseArmortoolsTime,float,0.1,,\n"
        gamevar += "ReviveTimeout,ReviveTimeout,int,1,,\n"
        gamevar += "StropUseCooldown,StropUseCooldown,float,0,,\n"
        gamevar += "SwitchStropCD,SwitchStropCD,float,0,,\n"
        gamevar += "StropBoostCooldown,StropBoostCooldown,float,0,,"
    
    # Add bypass (anti-ban)
    if user_prefs.get('BYPASSV1'):
        gamevar += "\nCheckHacker,CheckHacker,bool,false,,\n"
        gamevar += "DebugHack,DebugHack,bool,true,,\n"
        gamevar += "TestModeEnabled,TestModeEnabled,bool,true,,\n"
        gamevar += "DisableGinInfoSend,DisableGinInfoSend,int,1,,\n"
        gamevar += "CleanFFAntiState,CleanFFAntiState,bool,true,,"
    
    # Update the config
    config['gamevar'] = gamevar
    
    # Return the modified config
    response = Response(
        json.dumps(config),
        status=200,
        mimetype='application/json'
    )
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

# ============================================================
# TOGGLE API - For the web UI
# ============================================================
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

# ============================================================
# WEB UI - Copy his design
# ============================================================
@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>YOUR MODS</title>
    <style>
        body { background: #0a0a0f; color: #fff; font-family: sans-serif; padding: 20px; }
        .toggle-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; max-width: 500px; margin: auto; }
        .toggle-item { background: #1a1a2e; padding: 15px; border-radius: 10px; cursor: pointer; border: 1px solid #333; }
        .toggle-item.active { border-color: #4fc3f7; }
        .toggle-item .label { font-size: 14px; font-weight: 600; }
        .toggle-item .toggle-switch { float: right; width: 40px; height: 22px; background: #333; border-radius: 11px; position: relative; }
        .toggle-item .toggle-switch::after { content: ''; position: absolute; width: 18px; height: 18px; background: #666; border-radius: 50%; top: 2px; left: 2px; transition: 0.3s; }
        .toggle-item.active .toggle-switch { background: #4fc3f7; }
        .toggle-item.active .toggle-switch::after { left: 20px; background: #fff; }
    </style>
    </head>
    <body>
    <h1>🎮 YOUR MODS</h1>
    <div class="toggle-grid" id="toggleGrid"></div>
    <p style="text-align:center;margin-top:20px;color:#666;">Restart game after changing settings</p>
    <script>
        const toggles = {
            HS_NECK: { label: 'HS NECK', desc: 'Neck shots = headshot' },
            HS_CHEST: { label: 'HS CHEST', desc: 'Chest shots = headshot' },
            SPEED_HACK: { label: 'SPEED HACK', desc: '2x movement speed' },
            BACKJUMPV1: { label: 'BACK JUMP', desc: 'Old back jump mechanic' },
            NO_SWAP: { label: 'NO SWAP', desc: 'Instant weapon swap' },
            BYPASSV1: { label: 'BYPASS', desc: 'Anti-ban protection' },
            HIGH_JUMP: { label: 'HIGH JUMP', desc: 'Increased jump height' },
            NO_CD_MICS: { label: 'NO CD MICS', desc: 'No cooldown + fast landing' },
            RAPID_FIRE: { label: 'RAPID FIRE', desc: 'Increased fire rate' },
            HIGH_FPS: { label: 'HIGH FPS', desc: 'Frame rate auto boost' },
            HIGH_SENSI: { label: 'HIGH SENSI', desc: 'Sensitivity set to 999' }
        };
        
        async function loadConfig() {
            const resp = await fetch('/api/config');
            const config = await resp.json();
            const grid = document.getElementById('toggleGrid');
            grid.innerHTML = '';
            for (const [key, data] of Object.entries(toggles)) {
                const div = document.createElement('div');
                div.className = 'toggle-item' + (config[key] ? ' active' : '');
                div.innerHTML = `<div class="label">${data.label}</div><div class="toggle-switch"></div><div style="font-size:11px;color:#888;margin-top:4px;">${data.desc}</div>`;
                div.onclick = async () => {
                    div.classList.toggle('active');
                    const newState = div.classList.contains('active');
                    config[key] = newState;
                    await fetch('/api/config', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(config) });
                };
                grid.appendChild(div);
            }
        }
        loadConfig();
    </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
