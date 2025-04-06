from flask import Flask, request, jsonify
import secrets
from functools import wraps
import ssl

app = Flask(__name__)

# Generate a strong API key (store this securely)
API_KEY = secrets.token_urlsafe(32)
with open('.env', 'w') as f:
    f.write(API_KEY)

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key and api_key == API_KEY:
            return f(*args, **kwargs)
        return jsonify({"error": "Unauthorized"}), 401
    return decorated

@app.route('/echo', methods=['POST'])
@require_api_key
def echo():
    data = request.json
    message = data.get('message', '')
    return jsonify({'response': message})

if __name__ == '__main__':
    # Use HTTPS with self-signed certificate for development
    # For production, use proper certificates from Let's Encrypt or similar
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('cert.pem', 'key.pem')
    
    app.run(host='0.0.0.0', port=5000, ssl_context=context)
