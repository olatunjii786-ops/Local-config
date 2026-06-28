from flask import Flask, request, Response
import json
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# ============================================================
# HIS EXACT CONFIG - COPIED PERFECTLY
# ============================================================
@app.route('/ver.php', methods=['GET', 'POST'])
def serve_config():
    logging.info(f"Request from: {request.remote_addr}")
    
    # HIS EXACT JSON - DO NOT MODIFY
    config = {
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
        "gamevar": "var_name,comment,var_type,var_value\nvar_name,comment,\"var_type float, int, bool\",var_value\nANODisabledRegions,\u5173\u95edMTP\u7684\u5730\u533a,string,\"IND,NA\"\nANODisabledClientVariant,ANODisabledClientVariant,string,\"ClientUsingVersion_MAX_HPE,ClientUsingVersion_FFI,ClientUsingVersion_MAX|IND,ClientUsingVersion_MAX|NA,ClientUsingVersion_NORMAL|NA\"\nEnableMtpLiteDataRegion,mtp\u8f7b\u7279\u5f81\u5f00\u5173,string,\"BR,EUROPE,ID,ME,US,RU,SAC,SG,TH,TW,VN,PK,ZA,BD\"\nANOEmulatorCheckDisbaledClientVariant,ANOEmulatorCheckDisbaledClientVariant,string,\"ClientUsingVersion_FFI,ClientUsingVersion_MAX,ClientUsingVersion_NORMAL\"\nForceTutorial_ChangeHudABTest,fps\u6d41\u7a0b\u4e2d\u6253\u5f00hud\u9009\u62e9\u754c\u9762\u7684\u6982\u7387,float,-1\n\nCleanFFAntiState,CleanFFAntiState,bool,true,,\nFFAntihackDefenceLevel,FFAntihackDefenceLevel,string,0,,\nFFAntihackLightInitOnThread,FFAntihackLightInitOnThread,bool,false,,\nFFAntihackEmulatorCheckDisbaledClientVariant,FFAntihackEmulatorCheckDisbaledClientVariant,string,,,\nFFAntihackSDKDetailEncryptBySHA1,FFAntihackSDKDetailEncryptBySHA1,bool,false,,\nEnableFFAntihackInfoExtra,EnableFFAntihackInfoExtra,bool,false,,\nCheckHacker,CheckHacker,bool,false,,\nDebugHack,DebugHack,bool,true,,\nTestModeEnabled,TestModeEnabled,bool,true,,\nEarlyInitGGP,EarlyInitGGP,bool,false,,\nDisableGinInfoSend,DisableGinInfoSend,int,1,,\nGinInfoBRAliveThreshold,GinInfoBRAliveThreshold,int,0,,\nAntiHackResetSubgameInterval,AntiHackResetSubgameInterval,int,0,,\nFFANTIHACKEXT_SPLIT_THRESHOLD,FFANTIHACKEXT_SPLIT_THRESHOLD,int,0,,\nNeedProcessAH,NeedProcessAH,bool,true,,\nEnablePlatformCheck,EnablePlatformCheck,bool,false,,\nEnableSupCheck,EnableSupCheck,bool,false,,\nEnableMMKPlatformCheck,EnableMMKPlatformCheck,bool,false,,\nShowHighFrameRateSetting,ShowHighFrameRateSetting,bool,true,,\nReal60FrameSwitch,Real60FrameSwitch,bool,true,,\nIsAlbumScreenShotNeedAntiMod,IsAlbumScreenShotNeedAntiMod,bool,false,,\nEnableIceWallHacker,EnableIceWallHacker,bool,true,,\nEnableIceWallHackerKill,EnableIceWallHackerKill,bool,true,,\nEnableHipHackerKill,EnableHipHackerKill,bool,true,,\nEnableSendHackStoreLog,EnableSendHackStoreLog,bool,false,,\nGGPLoginOnce,GGPLoginOnce,bool,true,,\nEnableIngameQuickReport,EnableIngameQuickReport,bool,false,,\nEnableBugReportTime,EnableBugReportTime,bool,false,,\nEnableGGPOnLowMemory,EnableGGPOnLowMemory,bool,true,,\nReportee_Damager_RecentlyMaxCnt,Reportee_Damager_RecentlyMaxCnt,int,0,,\nReportee_Killer_RecentlyMaxCnt,Reportee_Killer_RecentlyMaxCnt,int,0,,\nGGPUpdateFlag,GGPUpdateFlag,int,0,,\nSwapWeaponCD,SwapWeaponCD,float,0,,\nSwitchWeaponInterval,SwitchWeaponInterval,float,0,,\nReloadTimeMultiplier,ReloadTimeMultiplier,float,0.1,,",
        "device_whitelist_version": "1.6.0",
        "whitelist_mask": 0,
        "device_whitelist_sp_version": "1.0.0",
        "whitelist_sp_mask": 0,
        "ggp_url": "na-gin.freefiremobile.com",
        "cdn_url": "http://localhost:5000/cdn/live/ABHotUpdates/",
        "backup_cdn_url": "http://localhost:5000/cdn/live/ABHotUpdates/",
        "abhotupdate_cdn_url": "http://localhost:5000/cdn/live/ABHotUpdates/"
    }
    
    # Convert to JSON string with NO EXTRA SPACES
    json_str = json.dumps(config, separators=(',', ':'), ensure_ascii=False)
    
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
    
    logging.info(f"Response length: {len(json_str)} bytes")
    return response

# ============================================================
# WEB UI
# ============================================================
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
        .important { border-color: rgba(255,50,50,0.3); }
        .important .label { color: #ff6b6b; }
        .important.active { border-color: #ff6b6b; }
        .important.active .toggle-switch { background: #ff6b6b; border-color: #ff6b6b; }
    </style>
    </head>
    <body>
    <div class="status">🟢 Proxy Active</div>
    <div class="toggle-grid" id="toggleGrid"></div>
    <p style="text-align:center;margin-top:20px;color:#666;">Restart game after changing settings</p>
    <script>
        const toggles = {
            HS_NECK: { label: 'HS NECK', desc: 'Neck shots = headshot' },
            HS_CHEST: { label: 'HS CHEST', desc: 'Chest shots = headshot' },
            SPEED_HACK: { label: 'SPEED HACK', desc: '2x movement speed' },
            BACKJUMPV1: { label: 'BACK JUMP', desc: 'Old back jump mechanic' },
            NO_SWAP: { label: 'NO SWAP', desc: 'Instant weapon swap' },
            BYPASSV1: { label: 'BYPASS', desc: 'Anti-ban protection', important: true },
            HIGH_JUMP: { label: 'HIGH JUMP', desc: 'Increased jump height' },
            NO_CD_MICS: { label: 'NO CD MICS', desc: 'No cooldown + fast landing' },
            RAPID_FIRE: { label: 'RAPID FIRE', desc: 'Increased fire rate' },
            HIGH_FPS: { label: 'HIGH FPS', desc: 'Frame rate auto boost' },
            HIGH_SENSI: { label: 'HIGH SENSI', desc: 'Sensitivity set to 999' }
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
                    div.innerHTML = `<div class="label">${data.label}</div><div class="toggle-switch"></div><div style="font-size:11px;color:#888;margin-top:4px;">${data.desc}</div>`;
                    div.onclick = async () => {
                        div.classList.toggle('active');
                        const newState = div.classList.contains('active');
                        config[key] = newState;
                        await fetch('/api/config', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(config) });
                    };
                    grid.appendChild(div);
                }
            } catch(e) {
                console.error('Error loading config:', e);
            }
        }
        loadConfig();
    </script>
    </body>
    </html>
    '''

# ============================================================
# TOGGLE API
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
