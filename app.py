from flask import Flask, request, Response, jsonify
import requests
import json
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# ============================================================
# USE HIS SERVER AS THE SOURCE
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

# ============================================================
# CLEAN GAMEVAR BUILDER
# ============================================================
def build_clean_gamevar(base_gamevar):
    """Extract only the essential fields and add features"""
    
    # Start with a clean base that we know works
    clean_gamevar = [
        "var_name,comment,var_type,var_value",
        'var_name,comment,"var_type float, int, bool",var_value',
        'ANODisabledRegions,关闭MTP的地区,string,"IND,NA"',
        'ANODisabledClientVariant,ANODisabledClientVariant,string,"ClientUsingVersion_MAX_HPE,ClientUsingVersion_FFI,ClientUsingVersion_MAX|IND,ClientUsingVersion_MAX|NA,ClientUsingVersion_NORMAL|NA"',
        'EnableMtpLiteDataRegion,mtp轻特征开关,string,"BR,EUROPE,ID,ME,US,RU,SAC,SG,TH,TW,VN,PK,ZA,BD"',
        'ANOEmulatorCheckDisbaledClientVariant,ANOEmulatorCheckDisbaledClientVariant,string,"ClientUsingVersion_FFI,ClientUsingVersion_MAX,ClientUsingVersion_NORMAL"',
        'ForceTutorial_ChangeHudABTest,fps流程中打开hud选择界面的概率,float,-1',
        '',
        'CleanFFAntiState,CleanFFAntiState,bool,true,,',
        'FFAntihackDefenceLevel,FFAntihackDefenceLevel,string,0,,',
        'FFAntihackLightInitOnThread,FFAntihackLightInitOnThread,bool,false,,',
        'FFAntihackEmulatorCheckDisbaledClientVariant,FFAntihackEmulatorCheckDisbaledClientVariant,string,,,',
        'FFAntihackSDKDetailEncryptBySHA1,FFAntihackSDKDetailEncryptBySHA1,bool,false,,',
        'EnableFFAntihackInfoExtra,EnableFFAntihackInfoExtra,bool,false,,',
        'CheckHacker,CheckHacker,bool,false,,',
        'DebugHack,DebugHack,bool,true,,',
        'TestModeEnabled,TestModeEnabled,bool,true,,',
        'EarlyInitGGP,EarlyInitGGP,bool,false,,',
        'DisableGinInfoSend,DisableGinInfoSend,int,1,,',
        'GinInfoBRAliveThreshold,GinInfoBRAliveThreshold,int,0,,',
        'AntiHackResetSubgameInterval,AntiHackResetSubgameInterval,int,0,,',
        'FFANTIHACKEXT_SPLIT_THRESHOLD,FFANTIHACKEXT_SPLIT_THRESHOLD,int,0,,',
        'NeedProcessAH,NeedProcessAH,bool,true,,',
        'EnablePlatformCheck,EnablePlatformCheck,bool,false,,',
        'EnableSupCheck,EnableSupCheck,bool,false,,',
        'EnableMMKPlatformCheck,EnableMMKPlatformCheck,bool,false,,',
        'ShowHighFrameRateSetting,ShowHighFrameRateSetting,bool,true,,',
        'Real60FrameSwitch,Real60FrameSwitch,bool,true,,',
        'IsAlbumScreenShotNeedAntiMod,IsAlbumScreenShotNeedAntiMod,bool,false,,',
        'EnableIceWallHacker,EnableIceWallHacker,bool,true,,',
        'EnableIceWallHackerKill,EnableIceWallHackerKill,bool,true,,',
        'EnableHipHackerKill,EnableHipHackerKill,bool,true,,',
        'EnableSendHackStoreLog,EnableSendHackStoreLog,bool,false,,',
        'GGPLoginOnce,GGPLoginOnce,bool,true,,',
        'EnableIngameQuickReport,EnableIngameQuickReport,bool,false,,',
        'EnableBugReportTime,EnableBugReportTime,bool,false,,',
        'EnableGGPOnLowMemory,EnableGGPOnLowMemory,bool,true,,',
        'Reportee_Damager_RecentlyMaxCnt,Reportee_Damager_RecentlyMaxCnt,int,0,,',
        'Reportee_Killer_RecentlyMaxCnt,Reportee_Killer_RecentlyMaxCnt,int,0,,',
        'GGPUpdateFlag,GGPUpdateFlag,int,0,,'
    ]
    
    # Add features based on toggles
    if user_prefs.get('HS_NECK') or user_prefs.get('HS_CHEST'):
        clean_gamevar.append('EnableHeadshotOnly,EnableHeadshotOnly,bool,true,,')
        clean_gamevar.append('HeadshotMultiplier,HeadshotMultiplier,float,999.0,,')
        clean_gamevar.append('OneShotKill,OneShotKill,bool,true,,')
        clean_gamevar.append('DamageMultiplier,DamageMultiplier,float,999.0,,')
    
    if user_prefs.get('SPEED_HACK'):
        clean_gamevar.append('SpeedMultiplier,SpeedMultiplier,float,2.0,,')
        clean_gamevar.append('RunSpeedMultiplier,RunSpeedMultiplier,float,2.0,,')
    
    if user_prefs.get('HIGH_JUMP'):
        clean_gamevar.append('MaxJumpHeight,MaxJumpHeight,float,999,,')
        clean_gamevar.append('JumpHeightMultiplier,JumpHeightMultiplier,float,5.0,,')
    
    if user_prefs.get('RAPID_FIRE'):
        clean_gamevar.append('FireRateMultiplier,FireRateMultiplier,float,2.0,,')
        clean_gamevar.append('OneShotLimitInOneFrame,OneShotLimitInOneFrame,int,999,,')
    
    if user_prefs.get('NO_CD_MICS'):
        clean_gamevar.append('UseMedkitTime,UseMedkitTime,float,0.1,,')
        clean_gamevar.append('UseArmortoolsTime,UseArmortoolsTime,float,0.1,,')
        clean_gamevar.append('ReviveTimeout,ReviveTimeout,int,1,,')
        clean_gamevar.append('StropUseCooldown,StropUseCooldown,float,0,,')
        clean_gamevar.append('SwitchStropCD,SwitchStropCD,float,0,,')
        clean_gamevar.append('StropBoostCooldown,StropBoostCooldown,float,0,,')
    
    if user_prefs.get('NO_SWAP'):
        clean_gamevar.append('SwapWeaponCD,SwapWeaponCD,float,0,,')
        clean_gamevar.append('SwitchWeaponInterval,SwitchWeaponInterval,float,0,,')
        clean_gamevar.append('ReloadTimeMultiplier,ReloadTimeMultiplier,float,0.1,,')
    
    if user_prefs.get('HIGH_SENSI'):
        clean_gamevar.append('SensitivityMaxSetting,SensitivityMaxSetting,float,999.0,,')
        clean_gamevar.append('Sensitivity1PMaxSetting,Sensitivity1PMaxSetting,float,999.0,,')
        clean_gamevar.append('X1ScopeMaxSetting,X1ScopeMaxSetting,float,999.0,,')
        clean_gamevar.append('X2ScopeMaxSetting,X2ScopeMaxSetting,float,999.0,,')
        clean_gamevar.append('X4ScopeMaxSetting,X4ScopeMaxSetting,float,999.0,,')
        clean_gamevar.append('X8ScopeMaxSetting,X8ScopeMaxSetting,float,999.0,,')
        clean_gamevar.append('FreeLookMaxSetting,FreeLookMaxSetting,float,999.0,,')
    
    if user_prefs.get('BYPASSV1'):
        clean_gamevar.append('CheckHacker,CheckHacker,bool,false,,')
        clean_gamevar.append('DebugHack,DebugHack,bool,true,,')
        clean_gamevar.append('TestModeEnabled,TestModeEnabled,bool,true,,')
        clean_gamevar.append('DisableGinInfoSend,DisableGinInfoSend,int,1,,')
        clean_gamevar.append('CleanFFAntiState,CleanFFAntiState,bool,true,,')
    
    return "\n".join(clean_gamevar)

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
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }
    
    try:
        # Fetch from his server
        logging.info(f"Fetching from: {SOURCE_URL}")
        response = requests.get(SOURCE_URL, params=params, headers=headers, timeout=10)
        logging.info(f"Source response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                config = response.json()
                logging.info("Got config from source server")
                
                # Rebuild clean gamevar
                if 'gamevar' in config:
                    config['gamevar'] = build_clean_gamevar(config['gamevar'])
                    logging.info("Built clean gamevar with features")
                
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

# ============================================================
# API CONFIG
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
