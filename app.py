from flask import Flask, jsonify, render_template, request
import json
import os

app = Flask(__name__)

# Load config from file
def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except:
        return {"code": 2, "use_login_optional_download": False}

@app.route('/')
def home():
    """Return a nice HTML page for visitors"""
    return render_template('index.html')

@app.route('/ver.php')
def serve_config():
    """Serve the config.json for the game"""
    config = load_config()
    
    # Log the request (helps debugging)
    print(f"Request from: {request.remote_addr}")
    print(f"User-Agent: {request.headers.get('User-Agent')}")
    print(f"Full URL: {request.url}")
    
    return jsonify(config)

@app.route('/ver.php', methods=['POST'])
def serve_config_post():
    """Handle POST requests too"""
    return serve_config()

@app.route('/config')
def serve_config_alt():
    """Alternative route if game requests /config"""
    return serve_config()

@app.route('/health')
def health():
    """Health check for Render"""
    return {"status": "ok", "message": "Server is running"}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
