from flask import Flask, jsonify, render_template, request, Response
import json
import os
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load config from file
def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error("config.json not found!")
        return {"code": 0, "message": "config not found"}
    except json.JSONDecodeError:
        logging.error("Invalid JSON in config.json!")
        return {"code": 0, "message": "invalid config"}

# ============================================================
# MAIN CONFIG ENDPOINT - Serves JSON with proper headers
# ============================================================
def serve_config():
    config = load_config()
    
    # Create response with proper headers
    response = Response(
        json.dumps(config),
        status=200,
        mimetype='application/json'
    )
    
    # Headers the game expects
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response

# ============================================================
# ROUTES - The game tries both of these
# ============================================================

@app.route('/ver.php')
def serve_config_via_php():
    """Route 1: The original ver.php endpoint"""
    logging.info(f"Request from: {request.remote_addr} via /ver.php")
    return serve_config()

@app.route('/api/config')
def serve_config_via_api():
    """Route 2: The API endpoint (this is what his server has!)"""
    logging.info(f"Request from: {request.remote_addr} via /api/config")
    return serve_config()

@app.route('/config')
def serve_config_alt():
    """Fallback: /config route (just in case)"""
    return serve_config()

@app.route('/config.json')
def serve_config_json():
    """Fallback: /config.json route (just in case)"""
    return serve_config()

# ============================================================
# WEB INTERFACE - Shows a nice page for visitors
# ============================================================

@app.route('/')
def home():
    """Main page with proxy control panel style"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check for Render"""
    return jsonify({"status": "ok", "message": "Server is running"})

# ============================================================
# ERROR HANDLING
# ============================================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Server error"}), 500

# ============================================================
# RUN THE SERVER
# ============================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
