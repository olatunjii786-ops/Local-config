from flask import Flask, request, jsonify, Response
import requests
import json
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

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

# ============================================================
# THE EXACT CONFIG FROM HIS SERVER
# ============================================================
BASE_CONFIG = {
    "code": 2,
    "use_login_optional_download": False,
    "use_background_download": False,
    "use_background_download_lobby": False,
    "country_code": "US",
    "client_ip": "74.220.48.30",
    "gdpr_version": 0,
    "billboard_cdn_url": "",
    "billboard_msg": "",
    "web_url": "",
    "billboard_bg_url": "",
    "max_store": "",
    "max_web": "",
    "max_video": "",
    "patchnote_url": "",
    "multi_region": "",
    "appstore_url": "http://www.freefiremobile.com/",
    "backup_appstore_url": "",
    "garena_login": False,
    "garena_hint": False,
    "gop_url": "",
    "device_whitelist_version": "1.6.0",
    "whitelist_mask": 0,
    "device_whitelist_sp_version": "1.0.0",
    "whitelist_sp_mask": 0,
    "ggp_url": "na-gin.freefiremobile.com",
    "cdn_url": "http://localhost:5000/cdn/live/ABHotUpdates/",
    "backup_cdn_url": "http://localhost:5000/cdn/live/ABHotUpdates/",
    "abhotupdate_cdn_url": "http://localhost:5000/cdn/live/ABHotUpdates/"
}

# ============================================================
# BUILD THE GAMEVAR STRING (Matching His Exactly)
# ============================================================
def build_gamevar():
    gamevar = """var_name,comment,var_type,var_value
var_name,comment,"var_type float, int, bool",var_value
ANODisabledRegions,关闭MTP的地区,string,"IND,NA"
ANODisabledClientVariant,ANODisabledClientVariant,string,"ClientUsingVersion_MAX_HPE,ClientUsingVersion_FFI,ClientUsingVersion_MAX|IND,ClientUsingVersion_MAX|NA,ClientUsingVersion_NORMAL|NA"
EnableMtpLiteDataRegion,mtp轻特征开关,string,"BR,EUROPE,ID,ME,US,RU,SAC,SG,TH,TW,VN,PK,ZA,BD"
ANOEmulatorCheckDisbaledClientVariant,ANOEmulatorCheckDisbaledClientVariant,string,"ClientUsingVersion_FFI,ClientUsingVersion_MAX,ClientUsingVersion_NORMAL"
ForceTutorial_ChangeHudABTest,fps流程中打开hud选择界面的概率,float,-1

CleanFFAntiState,CleanFFAntiState,bool,true,,
FFAntihackDefenceLevel,FFAntihackDefenceLevel,string,0,,
FFAntihackLightInitOnThread,FFAntihackLightInitOnThread,bool,false,,
FFAntihackEmulatorCheckDisbaledClientVariant,FFAntihackEmulatorCheckDisbaledClientVariant,string,,,
FFAntihackSDKDetailEncryptBySHA1,FFAntihackSDKDetailEncryptBySHA1,bool,false,,
EnableFFAntihackInfoExtra,EnableFFAntihackInfoExtra,bool,false,,
CheckHacker,CheckHacker,bool,false,,
DebugHack,DebugHack,bool,true,,
TestModeEnabled,TestModeEnabled,bool,true,,
EarlyInitGGP,EarlyInitGGP,bool,false,,
DisableGinInfoSend,DisableGinInfoSend,int,1,,
GinInfoBRAliveThreshold,GinInfoBRAliveThreshold,int,0,,
AntiHackResetSubgameInterval,AntiHackResetSubgameInterval,int,0,,
FFANTIHACKEXT_SPLIT_THRESHOLD,FFANTIHACKEXT_SPLIT_THRESHOLD,int,0,,
NeedProcessAH,NeedProcessAH,bool,true,,
EnablePlatformCheck,EnablePlatformCheck,bool,false,,
EnableSupCheck,EnableSupCheck,bool,false,,
EnableMMKPlatformCheck,EnableMMKPlatformCheck,bool,false,,
ShowHighFrameRateSetting,ShowHighFrameRateSetting,bool,true,,
Real60FrameSwitch,Real60FrameSwitch,bool,true,,
IsAlbumScreenShotNeedAntiMod,IsAlbumScreenShotNeedAntiMod,bool,false,,
EnableIceWallHacker,EnableIceWallHacker,bool,true,,
EnableIceWallHackerKill,EnableIceWallHackerKill,bool,true,,
EnableHipHackerKill,EnableHipHackerKill,bool,true,,
EnableSendHackStoreLog,EnableSendHackStoreLog,bool,false,,
GGPLoginOnce,GGPLoginOnce,bool,true,,
EnableIngameQuickReport,EnableIngameQuickReport,bool,false,,
EnableBugReportTime,EnableBugReportTime,bool,false,,
EnableGGPOnLowMemory,EnableGGPOnLowMemory,bool,true,,
Reportee_Damager_RecentlyMaxCnt,Reportee_Damager_RecentlyMaxCnt,int,0,,
Reportee_Killer_RecentlyMaxCnt,Reportee_Killer_RecentlyMaxCnt,int,0,,
GGPUpdateFlag,GGPUpdateFlag,int,0,,
SwapWeaponCD,SwapWeaponCD,float,0,,
SwitchWeaponInterval,SwitchWeaponInterval,float,0,,
ReloadTimeMultiplier,ReloadTimeMultiplier,float,0.1,,"""
    
    # Add features based on toggles
    if user_prefs.get('HS_NECK') or user_prefs.get('HS_CHEST'):
        gamevar += "\nEnableHeadshotOnly,EnableHeadshotOnly,bool,true,,\nHeadshotMultiplier,HeadshotMultiplier,float,999.0,,\nOneShotKill,OneShotKill,bool,true,,\nDamageMultiplier,DamageMultiplier,float,999.0,,"
    
    if user_prefs.get('SPEED_HACK'):
        gamevar += "\nSpeedMultiplier,SpeedMultiplier,float,2.0,,\nRunSpeedMultiplier,RunSpeedMultiplier,float,2.0,,"
    
    if user_prefs.get('HIGH_JUMP'):
        gamevar += "\nMaxJumpHeight,MaxJumpHeight,float,999,,\nJumpHeightMultiplier,JumpHeightMultiplier,float,5.0,,"
    
    if user_prefs.get('RAPID_FIRE'):
        gamevar += "\nFireRateMultiplier,FireRateMultiplier,float,2.0,,\nOneShotLimitInOneFrame,OneShotLimitInOneFrame,int,999,,"
    
    if user_prefs.get('NO_CD_MICS'):
        gamevar += "\nUseMedkitTime,UseMedkitTime,float,0.1,,\nUseArmortoolsTime,UseArmortoolsTime,float,0.1,,\nReviveTimeout,ReviveTimeout,int,1,,\nStropUseCooldown,StropUseCooldown,float,0,,\nSwitchStropCD,SwitchStropCD,float,0,,\nStropBoostCooldown,StropBoostCooldown,float,0,,"
    
    if user_prefs.get('NO_SWAP'):
        gamevar += "\nSwapWeaponCD,SwapWeaponCD,float,0,,\nSwitchWeaponInterval,SwitchWeaponInterval,float,0,,\nReloadTimeMultiplier,ReloadTimeMultiplier,float,0.1,,"
    
    if user_prefs.get('HIGH_SENSI'):
        gamevar += "\nSensitivityMaxSetting,SensitivityMaxSetting,float,999.0,,\nSensitivity1PMaxSetting,Sensitivity1PMaxSetting,float,999.0,,\nX1ScopeMaxSetting,X1ScopeMaxSetting,float,999.0,,\nX2ScopeMaxSetting,X2ScopeMaxSetting,float,999.0,,\nX4ScopeMaxSetting,X4ScopeMaxSetting,float,999.0,,\nX8ScopeMaxSetting,X8ScopeMaxSetting,float,999.0,,\nFreeLookMaxSetting,FreeLookMaxSetting,float,999.0,,"
    
    if user_prefs.get('BYPASSV1'):
        gamevar += "\nCheckHacker,CheckHacker,bool,false,,\nDebugHack,DebugHack,bool,true,,\nTestModeEnabled,TestModeEnabled,bool,true,,\nDisableGinInfoSend,DisableGinInfoSend,int,1,,\nCleanFFAntiState,CleanFFAntiState,bool,true,,"
    
    return gamevar

# ============================================================
# THE PROXY ENDPOINT - WITH EXACT HEADERS MATCHING HIS
# ============================================================
@app.route('/ver.php', methods=['GET', 'POST'])
def serve_config():
    logging.info(f"Request from: {request.remote_addr}")
    
    # Build the full config
    config = BASE_CONFIG.copy()
    config['gamevar'] = build_gamevar()
    
    # Convert to JSON string
    json_str = json.dumps(config)
    
    # ============================================================
    # EXACT HEADERS FROM HIS SERVER
    # ============================================================
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
    response.headers['Vary'] = 'Accept-Encoding'
    response.headers['Content-Length'] = str(len(json_str))
    
    logging.info(f"Response length: {len(json_str)} bytes")
    return response

# ============================================================
# TOGGLE API
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

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>NIKU MODS</title>
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
        .status { text-align: center; padding: 20px; color: #4fc3f7; }
    </style>
    </head>
    <body>
    <div class="status">🟢 Proxy Active: YOUR_SERVER_IP</div>
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
