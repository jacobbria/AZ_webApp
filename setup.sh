#!/bin/bash
# Azure VM Setup Script for Resume Webapp
# This script runs on Ubuntu 24.04 LTS during VM initialization
# It installs dependencies and starts the Flask app via Gunicorn

set -e

echo "=== Resume Webapp Azure Setup ==="
echo "Starting automated deployment..."

# Update system packages
echo "📦 Updating system packages..."
apt-get update
apt-get upgrade -y

# Install system dependencies
echo "📦 Installing system dependencies..."
apt-get install -y \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    supervisor \
    nginx

# Clone repository (update URL as needed)
echo "📥 Cloning repository..."
cd /opt
git clone https://github.com/jacobbria/resume_webapp_AZ.git || (cd resume_webapp_AZ && git pull)
cd resume_webapp_AZ

# Create Python virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Create data directory
mkdir -p data

# Initialize database with demo data
echo "💾 Initializing database..."
python3 -c "import db; db.init_db()"

# Configure Nginx as reverse proxy
echo "🔧 Configuring Nginx..."
cat > /etc/nginx/sites-available/resume_webapp << 'EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;

    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
}
EOF

# Enable the site
ln -sf /etc/nginx/sites-available/resume_webapp /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
echo "✓ Testing Nginx configuration..."
nginx -t

# Start Nginx
systemctl start nginx
systemctl enable nginx

# Configure Supervisor to manage Gunicorn
echo "🔧 Configuring Supervisor for Gunicorn..."
cat > /etc/supervisor/conf.d/resume_webapp.conf << 'EOF'
[program:resume_webapp]
directory=/opt/resume_webapp
command=/opt/resume_webapp/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 wsgi:app
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/resume_webapp.log
environment=FLASK_ENV=production
user=www-data
EOF

# Update Supervisor
supervisorctl reread
supervisorctl update
supervisorctl start resume_webapp

# Verify services
echo ""
echo "✅ Setup complete!"
echo ""
echo "Service Status:"
systemctl status nginx --no-pager
supervisorctl status resume_webapp

echo ""
echo "📊 Application accessible at: http://<your-public-ip>"
echo "📝 Logs available at: /var/log/resume_webapp.log"
echo ""
