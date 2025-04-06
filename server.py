from flask import Flask, request, jsonify
import secrets
from functools import wraps
import ssl
import os
import socket
import subprocess
from subprocess import Popen, PIPE

app = Flask(__name__)


def command(input):
    try:
        output = Popen(
            input,
            shell=True,
            stdout=PIPE,
            stderr=PIPE,
        )
        output = output.communicate()

        return output

    except Exception as e:
        print(e)
        pass


# Generate a strong API key (store this securely)
if os.path.exists(".env") is not True:
    print("Missing API key, generating new one...")
    with open(".env", "w") as api_key:
        api_key = api_key.write(f"ECHO_API_KEY={secrets.token_urlsafe(32)}")
        print("Generated new API key (make sure to share it with users!!!)")

# read api key from env
with open(".env", "r") as api_key:
    API_KEY = api_key.read().split("=")[-1]

# if missing a key generate new keys
if os.path.exists("cert.pem") is not True or os.path.exists("key.pem") is not True:
    print("Missing PEM keys, generating new ones!!!")
    # remove any existing keys
    if os.path.exists("cert.pem"):
        print("Deleting existing cert.pem")
        subprocess.run(["rm", "cert.pem"])
    if os.path.exists("key.pem"):
        print("Deleting existing key.pem")
        subprocess.run(["rm", "key.pem"])

    local_ip = str(socket.gethostbyname(socket.gethostname()))

    if local_ip == "127.0.0.1":
        print("Local IP is returning loopback, please advise...")
        exit()

    command_str = f'''openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365 \
-subj "/CN={local_ip}" \
-addext "subjectAltName = IP:{local_ip},IP:127.0.0.1,DNS:localhost"'''

    # generate pub/priv keys (cert.pem/key.pem respectively)
    command(command_str)


def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get("X-API-Key")
        if api_key and api_key == API_KEY:
            return f(*args, **kwargs)
        return jsonify({"error": "Unauthorized"}), 401

    return decorated


@app.route("/echo", methods=["POST"])
@require_api_key
def echo():
    data = request.json
    message = data.get("message", "")
    return jsonify({"response": message})


if __name__ == "__main__":
    # Use HTTPS with self-signed certificate for development
    # For production, use proper certificates from Let's Encrypt or similar
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain("cert.pem", "key.pem")

    app.run(host="0.0.0.0", port=5000, ssl_context=context)
