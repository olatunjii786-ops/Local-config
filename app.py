from flask import Flask, request, Response, jsonify
import requests
import json
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# ============================================================
# HIS SERVER ENDPOINTS
# ============================================================
HIS_CONFIG_URL = "https://niku-mods-proxy-1.onrender.com/ver.php"
HIS_API_URL = "https://niku-mods-proxy-1.onrender.com/api/config"

# ============================================================
# YOUR USER PREFERENCES (Mirror his toggles)
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
# PROXY HIS CONFIG (Forward game requests)
# ============================================================
@app.route('/ver.php', methods=['GET', 'POST'])
def proxy_ver_php():
    """Forward game config request to his server"""
    logging.info(f"Game request from: {request.remote_addr}")
    
    params = request.args.to_dict()
    headers = {
        'User-Agent': request.headers.get('User-Agent', 'UnityPlayer/2022.3.47f1'),
        'Accept': request.headers.get('Accept', '*/*'),
        'Connection': 'keep-alive',
    }
    
    try:
        response = requests.get(HIS_CONFIG_URL, params=params, headers=headers, timeout=10)
        logging.info(f"His server response: {response.status_code}")
        
        # Forward his response exactly as-is
        resp = Response(
            response.text,
            status=response.status_code,
            mimetype=response.headers.get('Content-Type', 'application/json')
        )
        
        # Forward his headers
        for key, value in response.headers.items():
            if key.lower() not in ['content-encoding', 'content-length', 'transfer-encoding']:
                resp.headers[key] = value
        
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
        
    except Exception as e:
        logging.error(f"Error: {e}")
        return jsonify({"code": 2, "message": "proxy error"}), 500

# ============================================================
# PROXY HIS TOGGLES (Forward your toggles to his API)
# ============================================================
@app.route('/api/config', methods=['GET', 'POST'])
def proxy_api_config():
    """Forward toggle changes to his server"""
    
    if request.method == 'POST':
        # Get your toggle data
        your_toggles = request.json
        logging.info(f"Your toggles: {your_toggles}")
        
        # Update your local prefs
        for key in your_toggles:
            if key in user_prefs:
                user_prefs[key] = your_toggles[key]
        
        # Forward the same toggles to his server
        try:
            his_response = requests.post(
                HIS_API_URL,
                json=your_toggles,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            logging.info(f"His API response: {his_response.status_code}")
            
            # Return his response
            return jsonify(his_response.json()), his_response.status_code
            
        except Exception as e:
            logging.error(f"Error forwarding to his API: {e}")
            return jsonify({"status": "ok", "prefs": user_prefs}), 200
    
    else:
        # GET request - return your prefs
        return jsonify(user_prefs)

# ============================================================
# YOUR DASHBOARD
# ============================================================
@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Proxy Control Panel</title>
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
            .toast { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background: #1a1a2e; padding: 12px 24px; border-radius: 10px; border: 1px solid #4fc3f7; display: none; z-index: 999; }
            @media (max-width: 400px) { .toggle-grid { grid-template-columns: 1fr; } }
        </style>
    </head>
    <body>
    <div class="container">
        <h1><i class="fas fa-bolt"></i> YOUR PROXY</h1>
        <p class="subtitle">Control His Toggles From Your Dashboard</p>
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
    app.run(host='0.0.0.0', port=5000)
