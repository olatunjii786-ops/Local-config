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
    
    # High FPS
    'ShowHighFrameRateSetting', 'Real60FrameSwitch', 'HighFPSSetting',
    
    # Rapid Fire (NUKED - REMOVED COMPLETELY)
    'FireInterval', 'FireRateMultiplier', 'OneShotLimitInOneFrame',
    'MaxAnimSpeed', 'RapidFire', 'Rapid_Fire',
    
    # Other unwanted
    'EnableAccelerationOnFalling', 'CanJumpFallingRunFast',
    'CanCreepRunFast', 'CanCrouchingRunFast', 'StropFallingResetSpeed',
]

# ============================================================
# FEATURES TO ADD (NO RAPID FIRE - ONLY REAL FEATURES)
# ============================================================
FEATURES_TO_ADD = [
    # ----- HEADSHOT (REAL - Found) -----
    'HeadShotOnly,HeadShotOnly,bool,true,,',
    'HeadShotMultiplier,HeadShotMultiplier,float,999.0,,',
    'HeadShotDamageScale,HeadShotDamageScale,float,999.0,,',
    
    # ----- BODY TO HEADSHOT (REAL - Found) -----
    'HitDamageRatioBody,HitDamageRatioBody,float,999.0,,',
    'HitDamageRatioHead,HitDamageRatioHead,float,999.0,,',
    'HitDamageRatioLimb,HitDamageRatioLimb,float,999.0,,',
    
    # ----- FAST RELOAD (REAL - Found) -----
    'ReloadSpeed,ReloadSpeed,float,999.0,,',
    'ReloadTimeMultiplier,ReloadTimeMultiplier,float,0.01,,',
    'FastAutoReloadSpeed,FastAutoReloadSpeed,float,999.0,,',
    'SwapWeaponCD,SwapWeaponCD,float,0.0,,',
    'SwitchWeaponInterval,SwitchWeaponInterval,float,0.0,,',
    
    # ----- UNLIMITED THROWABLES (REAL - Found) -----
    'UnlimitedThrowables,UnlimitedThrowables,bool,true,,',
    'UnlimitedThrowablesSwitch,UnlimitedThrowablesSwitch,bool,true,,',
    'unlimited_throwables_switch,unlimited_throwables_switch,bool,true,,',
    'MaxAutoPickupGrenade,MaxAutoPickupGrenade,int,99,,',
    'MaxAutoPickupFrozenGrenade,MaxAutoPickupFrozenGrenade,int,99,,',
    'MaxAutoPickupThrowingKnife,MaxAutoPickupThrowingKnife,int,99,,',
    
    # ----- UNLIMITED AMMO (REAL - Found) -----
    'UnlimitedAmmo,UnlimitedAmmo,bool,true,,',
    'UnlimitedAmmoSwitch,UnlimitedAmmoSwitch,bool,true,,',
    'unlimited_ammo_switch,unlimited_ammo_switch,bool,true,,',
    'AmmoFree,AmmoFree,bool,true,,',
    'FullAmmo,FullAmmo,bool,true,,',
    'AmmoClipSize,AmmoClipSize,int,999,,',
    'WeaponAmmoCilpRevise,WeaponAmmoCilpRevise,int,999,,',
    
    # ----- MAGIC BULLET (REAL - Found) -----
    'HitBoxScale,HitBoxScale,float,50.0,,',
    'HitboxScale,HitboxScale,float,50.0,,',
    'PlayerColliderRadius,PlayerColliderRadius,float,50.0,,',
    'BulletHitRadius,BulletHitRadius,float,50.0,,',
    'BulletHitBoxMultiplier,BulletHitBoxMultiplier,float,50.0,,',
    'ColliderScale,ColliderScale,float,50.0,,',
    'HitBoxMultiplier,HitBoxMultiplier,float,50.0,,',
    'HitBoxSizeMultiplier,HitBoxSizeMultiplier,float,50.0,,',
    'EnableHitBoxScale,EnableHitBoxScale,bool,true,,',
    'EnableFireColliderScale,EnableFireColliderScale,bool,true,,',
    'FireColliderRadiusScale,FireColliderRadiusScale,float,50.0,,',
    'FireColliderHeightScale,FireColliderHeightScale,float,50.0,,',
    'SantinoDummyColliderRadiusScale,SantinoDummyColliderRadiusScale,float,50.0,,',
    
    # ----- NO RECOIL (REAL - Found) -----
    'FPPRecoil,FPPRecoil,bool,false,,',
    'FPPRecoilYFactor,FPPRecoilYFactor,float,0.0,,',
    'FPPRecoilZFactor,FPPRecoilZFactor,float,0.0,,',
    'RecoilYCycle,RecoilYCycle,float,0.0,,',
    'RecoilZCycle,RecoilZCycle,float,0.0,,',
    'RecoilBackwardX,RecoilBackwardX,float,0.0,,',
    'RecoilBackwardZ,RecoilBackwardZ,float,0.0,,',
    'RecoilMultiplier,RecoilMultiplier,float,0.0,,',
    'RecoilAmount,RecoilAmount,float,0.0,,',
    'EnableRecoil,EnableRecoil,bool,false,,',
    
    # ----- NO SPREAD (REAL - Found) -----
    'NoSpread,NoSpread,bool,true,,',
    'SpreadMultiplier,SpreadMultiplier,float,0.0,,',
    'BulletSpread,BulletSpread,float,0.0,,',
    
    # ----- AIM ASSIST (REAL - Found) -----
    'AimAssistStrength,AimAssistStrength,float,999.0,,',
    'AimAssistRange,AimAssistRange,float,999.0,,',
    'AimAssistLockSpeed,AimAssistLockSpeed,float,999.0,,',
    'AimAssistLockDistance,AimAssistLockDistance,float,999.0,,',
    'EnableAimAssist,EnableAimAssist,bool,true,,',
]

# ============================================================
# NUKE FUNCTION - Remove unwanted, add missing features
# ============================================================
def nuke_and_add(gamevar):
    """Remove unwanted features and add missing ones (NO RAPID FIRE)"""
    
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
    
    # Add missing features (NO RAPID FIRE)
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
        .features { margin-top: 30px; text-align: left; max-width: 500px; margin-left: auto; margin-right: auto; }
        .features li { padding: 4px 0; }
        .removed { color: #ff6b6b; }
        .added { color: #4fc3f7; }
        .kept { color: #aaa; }
    </style>
    </head>
    <body>
    <div class="status">🟢 Proxy Active</div>
    <div class="info">All features from dump.cs (NO RAPID FIRE)</div>
    <div class="features">
        <h3 style="color:#fff;">Active Features:</h3>
        <ul style="list-style:none;padding:0;">
            <li class="added">✅ Headshot (HeadShotOnly, HeadShotMultiplier)</li>
            <li class="added">✅ Body-to-Headshot (HitDamageRatioBody)</li>
            <li class="added">✅ Fast Reload (ReloadSpeed, ReloadTimeMultiplier)</li>
            <li class="added">✅ Instant Weapon Swap (SwapWeaponCD)</li>
            <li class="added">✅ Unlimited Throwables (Grenades, Frozen, Throwing Knife)</li>
            <li class="added">✅ Unlimited Ammo (UnlimitedAmmo, AmmoFree)</li>
            <li class="added">✅ Magic Bullet (50x HitBoxScale)</li>
            <li class="added">✅ No Recoil (FPPRecoil, FPPRecoilYFactor)</li>
            <li class="added">✅ No Spread (NoSpread, SpreadMultiplier)</li>
            <li class="added">✅ Aim Assist (AimAssistStrength, AimAssistRange)</li>
            <li class="removed">❌ Speed, Jump, Back Jump, High Sensitivity</li>
            <li class="removed">❌ RAPID FIRE (REMOVED)</li>
            <li class="kept">✅ Everything else from his config preserved</li>
        </ul>
        <p style="color:#444;font-size:12px;margin-top:20px;">
            All features from dump.cs | NO RAPID FIRE | Diamonds are server-side (FAKE)
        </p>
    </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
