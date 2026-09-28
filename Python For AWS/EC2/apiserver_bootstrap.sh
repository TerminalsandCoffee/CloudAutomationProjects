#!/bin/bash
set -e

echo "Updating system..."
sudo apt update
sudo apt upgrade -y

echo "Installing packages..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    nginx \
    openssl \
    git

echo "Creating application directory..."
sudo mkdir -p /opt/api-demo
sudo chown $USER:$USER /opt/api-demo

cd /opt/api-demo

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install flask gunicorn

cat > app.py << 'EOF'
from flask import Flask, request, jsonify

app = Flask(__name__)

users = [
    {"id":1,"name":"Alice"},
    {"id":2,"name":"Bob"}
]

@app.route("/")
def home():
    return jsonify({"status":"running","service":"Demo API"})

@app.route("/users", methods=["GET"])
def get_users():
    return jsonify(users)

@app.route("/users/<int:id>", methods=["GET"])
def get_user(id):
    return jsonify({"id":id,"name":"Demo User"})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    return jsonify({
        "message":"Login Successful",
        "username":data.get("username")
    })

@app.route("/orders", methods=["GET"])
def orders():
    return jsonify([
        {"order":101},
        {"order":102}
    ])

@app.route("/payment", methods=["POST"])
def payment():
    return jsonify({
        "status":"Payment Accepted"
    })

@app.route("/health")
def health():
    return jsonify({"healthy":True})

if __name__ == "__main__":
    app.run()
EOF

cat > wsgi.py << EOF
from app import app
EOF

sudo tee /etc/systemd/system/apidemo.service > /dev/null << EOF
[Unit]
Description=Demo Flask API
After=network.target

[Service]
User=$USER
WorkingDirectory=/opt/api-demo
Environment="PATH=/opt/api-demo/venv/bin"
ExecStart=/opt/api-demo/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 wsgi:app

Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable apidemo
sudo systemctl restart apidemo

echo "Configuring TLS certificate for nginx (self-signed lab cert)..."
sudo mkdir -p /etc/nginx/ssl
# Always regenerate for lab idempotency (safe to re-run).
sudo openssl req -x509 -nodes -newkey rsa:2048 -days 365 \
    -keyout /etc/nginx/ssl/api-lab.key \
    -out /etc/nginx/ssl/api-lab.crt \
    -subj "/CN=api-lab.mscloudwaf.com"

sudo tee /etc/nginx/sites-available/apidemo > /dev/null << EOF
server {
    listen 80 default_server;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}

server {
    listen 443 ssl default_server;
    server_name _;

    ssl_certificate /etc/nginx/ssl/api-lab.crt;
    ssl_certificate_key /etc/nginx/ssl/api-lab.key;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/apidemo /etc/nginx/sites-enabled/apidemo
sudo rm -f /etc/nginx/sites-enabled/default

sudo nginx -t
sudo systemctl restart nginx

echo ""
echo "==================================="
echo "API Installed Successfully"
echo "==================================="
echo ""
echo "Endpoints:"
echo "/"
echo "/users"
echo "/users/1"
echo "/login"
echo "/orders"
echo "/payment"
echo "/health"
echo ""
echo "Verify locally:"
echo "  curl http://localhost/health"
echo "  curl -k https://localhost/health"
echo ""
echo "Security group must allow TCP 80 and 443."

# After, manually run:
# chmod +x apiserver_bootstrap.sh
# ./apiserver_bootstrap.sh
#
# curl http://localhost/health
# curl -k https://localhost/health
# curl http://<server-ip>/users
#
# Security group must allow TCP 80 and 443.
