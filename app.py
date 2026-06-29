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
    # Speed features (NUKED)
    'RunSpeed', 'DashSpeedScale', 'CrouchSpeed', 'CreepSpeed',
    'DieingSpeed', 'StropSpeed', 'HorseSpeedLineSpeed', 'HorseDeadSpeed',
    'SpeedMultiplier', 'RunSpeedMultiplier',
    
    # Jump features (NUKED)
    'MaxJumpHeight', 'JumpHeightMultiplier',
    'SkyDivingSpeedDelta', 'SkyDivingRotationSpeed', 'SkySurfingSpeedDelta',
    'ParachutingMaxAngleTilt', 'ParachutingMinAngleTilt',
    
    # Back jump (NUKED)
    'EnableBackJump', 'BackJumpSpeed',
    
    # High sensitivity (NUKED)
    'SensitivityMaxSetting', 'Sensitivity1PMaxSetting',
    'X1ScopeMaxSetting', 'X2ScopeMaxSetting', 'X4ScopeMaxSetting',
    'X8ScopeMaxSetting', 'FreeLookMaxSetting',
    
    # High FPS (NUKED)
    'ShowHighFrameRateSetting', 'Real60FrameSwitch', 'HighFPSSetting',
    
    # Rapid Fire (NUKED)
    'FireInterval', 'FireRateMultiplier', 'OneShotLimitInOneFrame',
    'MaxAnimSpeed', 'RapidFire',
    
    # Fake damage features (REMOVED - don't work)
    'DamageMultiplier', 'DamageRatioHead', 'DamageRatioBody',
    'DamageRatioLimb', 'MaxDamage', 'MinDamage', 'WeaponDamage',
    'BulletDamage', 'HeadShotDamageScale',
    
    # Fake unlimited features (REMOVED - don't work)
    'UnlimitedAmmo', 'UnlimitedAmmoSwitch', 'unlimited_ammo_switch',
    'AmmoFree', 'FullAmmo', 'AmmoClipSize', 'WeaponAmmoCilpRevise',
    'UnlimitedThrowables', 'UnlimitedThrowablesSwitch',
    'unlimited_throwables_switch', 'MaxAutoPickupGrenade',
    'MaxAutoPickupFrozenGrenade', 'MaxAutoPickupThrowingKnife',
    
    # Fake magic bullet (REMOVED - don't work)
    'HitBoxScale', 'HitboxScale', 'PlayerColliderRadius',
    'BulletHitRadius', 'BulletHitBoxMultiplier', 'ColliderScale',
    'HitBoxMultiplier', 'HitBoxSizeMultiplier', 'EnableHitBoxScale',
    'EnableFireColliderScale', 'FireColliderRadiusScale',
    'FireColliderHeightScale', 'SantinoDummyColliderRadiusScale',
    
    # Fake no recoil (REMOVED - don't work)
    'FPPRecoil', 'FPPRecoilYFactor', 'FPPRecoilZFactor',
    'RecoilYCycle', 'RecoilZCycle', 'RecoilBackwardX',
    'RecoilBackwardZ', 'RecoilMultiplier', 'RecoilAmount',
    'EnableRecoil',
    
    # Fake no spread (REMOVED - don't work)
    'NoSpread', 'SpreadMultiplier', 'BulletSpread',
    
    # Fake aim assist (REMOVED - don't work)
    'AimAssistStrength', 'AimAssistRange', 'AimAssistLockSpeed',
    'AimAssistLockDistance', 'EnableAimAssist',
    
    # Fake fast reload (REMOVED - visual only)
    'ReloadSpeed', 'ReloadTimeMultiplier', 'FastAutoReloadSpeed',
    'SwapWeaponCD', 'SwitchWeaponInterval',
    
    # Other unwanted
    'EnableAccelerationOnFalling', 'CanJumpFallingRunFast',
    'CanCreepRunFast', 'CanCrouchingRunFast', 'StropFallingResetSpeed',
]

# ============================================================
# ONLY KEEP FEATURES THAT ACTUALLY WORK
# ============================================================
FEATURES_TO_ADD = [
    # ----- ANTI-CHEAT BYPASS (REALLY WORKS) -----
    # These disable the client-side anti-cheat
    'CleanFFAntiState,CleanFFAntiState,bool,true,,',
    'FFAntihackDefenceLevel,FFAntihackDefenceLevel,string,0,,',
    'FFAntihackLightInitOnThread,FFAntihackLightInitOnThread,bool,false,,',
    'CheckHacker,CheckHacker,bool,false,,',
    'DebugHack,DebugHack,bool,true,,',
    'TestModeEnabled,TestModeEnabled,bool,true,,',
    'DisableGinInfoSend,DisableGinInfoSend,int,1,,',
    'EarlyInitGGP,EarlyInitGGP,bool,false,,',
    'EnableIceWallHacker,EnableIceWallHacker,bool,false,,',
    'EnableIceWallHackerKill,EnableIceWallHackerKill,bool,false,,',
    'EnableHipHackerKill,EnableHipHackerKill,bool,false,,',
    'EnableGGPOnLowMemory,EnableGGPOnLowMemory,bool,false,,',
    'GGPLoginOnce,GGPLoginOnce,bool,false,,',
    
    # ----- HEADSHOT (MIGHT work - depends on game version) -----
    'HeadShotOnly,HeadShotOnly,bool,true,,',
    'HeadShotMultiplier,HeadShotMultiplier,float,999.0,,',
]

# ============================================================
# NUKE FUNCTION
# ============================================================
def nuke_and_add(gamevar):
    """Remove unwanted features and add only working ones"""
    
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
    
    # Add only working features
    for feature in FEATURES_TO_ADD:
        logging.info(f"Adding: {feature}")
        cleaned_lines.append(feature)
    
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
        .features li { padding: 4px 0; }
        .removed { color: #ff6b6b; }
        .added { color: #4fc3f7; }
        .kept { color: #aaa; }
    </style>
    </head>
    <body>
    <div class="status">🟢 Proxy Active</div>
    <div class="info">Clean Config - Only Working Features</div>
    <div class="features">
        <h3 style="color:#fff;">Status:</h3>
        <ul style="list-style:none;padding:0;">
            <li class="added">✅ Anti-Cheat Bypass (CheckHacker, DebugHack)</li>
            <li class="added">✅ Test Mode (TestModeEnabled)</li>
            <li class="added">✅ GGP Disabled (DisableGinInfoSend)</li>
            <li class="added">✅ Headshot (HeadShotOnly, HeadShotMultiplier)</li>
            <li class="removed">❌ Speed, Jump, Back Jump, High Sensitivity</li>
            <li class="removed">❌ All Fake Features (Damage, Recoil, Spread, etc.)</li>
            <li class="kept">✅ Everything else from his config preserved</li>
        </ul>
        <p style="color:#444;font-size:12px;margin-top:20px;">
            Only features that actually work through config
        </p>
    </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
