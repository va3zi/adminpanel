#!/bin/bash

# VPN Admin Panel Installation Script
# This script automates the setup of the VPN Admin Panel on a Debian-based Linux server.
# It sets up PostgreSQL via Docker, the FastAPI backend, the Vue.js frontend, and Nginx as a reverse proxy.

# --- Configuration ---
PROJECT_DIR="/opt/vpn-admin-panel"
DB_CONTAINER_NAME="vpnpanel_postgres"
DB_USER="vpnpanel_user"
DB_NAME="vpnpanel_db"
# Passwords and domain will be requested interactively.

# --- Helper Functions ---
_header() {
    echo -e "\n\e[1;34m--- $1 ---\e[0m"
}

_error() {
    echo -e "\e[1;31mError: $1\e[0m" >&2
    exit 1
}

check_root() {
    if [ "$(id -u)" -ne 0 ]; then
        _error "This script must be run as root. Please use 'sudo bash install.sh'."
    fi
}

# --- Main Functions ---

get_user_input() {
    _header "Gathering Configuration Details"

    # Get Domain Name
    read -p "Enter the domain name for this panel (e.g., panel.example.com): " DOMAIN_NAME
    if [ -z "$DOMAIN_NAME" ]; then
        _error "Domain name cannot be empty."
    fi

    # Get other secrets securely
    read -sp "Enter the password for the panel's initial Super Admin: " PANEL_SUPERADMIN_PASSWORD
    echo
    if [ -z "$PANEL_SUPERADMIN_PASSWORD" ]; then
        _error "Panel Super Admin password cannot be empty."
    fi

    read -p "Enter the Marzban (Abresani) panel admin username: " MARZBAN_USERNAME
    if [ -z "$MARZBAN_USERNAME" ]; then
        _error "Marzban username cannot be empty."
    fi

    read -sp "Enter the Marzban (Abresani) panel admin password: " MARZBAN_PASSWORD
    echo
    if [ -z "$MARZBAN_PASSWORD" ]; then
        _error "Marzban password cannot be empty."
    fi

    read -p "Enter your Zarinpal Merchant ID: " ZARINPAL_MERCHANT_ID
    if [ -z "$ZARINPAL_MERCHANT_ID" ]; then
        _error "Zarinpal Merchant ID cannot be empty."
    fi
}

clone_project() {
    _header "Cloning Project Repository"
    if [ -d "$PROJECT_DIR" ]; then
        echo "Project directory already exists. Pulling latest changes..."
        cd "$PROJECT_DIR"
        git pull || _error "Failed to pull latest changes from git."
    else
        echo "Cloning repository into $PROJECT_DIR..."
        git clone https://github.com/va3zi/adminpanel.git "$PROJECT_DIR" || _error "Failed to clone repository."
    fi
}

check_dependencies() {
    _header "Checking and Installing Dependencies"
    PACKAGES="git docker.io python3-venv python3-pip nodejs npm nginx"
    for pkg in $PACKAGES; do
        if ! dpkg -l | grep -q "ii  $pkg "; then
            echo "$pkg is not installed. Attempting to install..."
            apt-get update -y || _error "Failed to update package lists."
            apt-get install -y "$pkg" || _error "Failed to install $pkg."
        else
            echo "$pkg is already installed."
        fi
    done

    # Ensure Docker service is running
    if ! systemctl is-active --quiet docker; then
        echo "Starting Docker service..."
        systemctl start docker
        systemctl enable docker
    fi

    echo "All dependencies are installed."
}

setup_database() {
    _header "Setting up MariaDB (MySQL) Database via Docker"

    # Securely ask for DB password
    read -sp "Please enter a strong password for the database user '$DB_USER': " DB_PASSWORD
    echo
    if [ -z "$DB_PASSWORD" ]; then
        _error "Database password cannot be empty."
    fi
    read -sp "Please enter the root password for the new MariaDB instance: " DB_ROOT_PASSWORD
    echo
    if [ -z "$DB_ROOT_PASSWORD" ]; then
        _error "MariaDB root password cannot be empty."
    fi

    echo "Pulling latest MariaDB Docker image..."
    docker pull mariadb:latest || _error "Failed to pull MariaDB image."

    echo "Stopping and removing any existing container named '$DB_CONTAINER_NAME'..."
    docker stop "$DB_CONTAINER_NAME" > /dev/null 2>&1
    docker rm "$DB_CONTAINER_NAME" > /dev/null 2>&1

    echo "Starting new MariaDB container..."
    docker run --name "$DB_CONTAINER_NAME" \
        -e MARIADB_ROOT_PASSWORD="$DB_ROOT_PASSWORD" \
        -e MARIADB_DATABASE="$DB_NAME" \
        -e MARIADB_USER="$DB_USER" \
        -e MARIADB_PASSWORD="$DB_PASSWORD" \
        -v "$PROJECT_DIR/mysql-data:/var/lib/mysql" \
        -p 3306:3306 \
        -d mariadb:latest || _error "Failed to start MariaDB container."

    echo "Waiting for database to initialize..."
    sleep 20

    echo "Database setup complete. MariaDB is running."
}


setup_backend() {
    _header "Setting up Backend"
    cd "$PROJECT_DIR/backend" || _error "Backend directory not found."

    echo "Creating Python virtual environment..."
    python3 -m venv venv || _error "Failed to create virtual environment."

    echo "Installing Python dependencies..."
    # Activate venv and install requirements
    source venv/bin/activate
    pip install -r requirements-dev.txt || _error "Failed to install Python dependencies."
    deactivate

    echo "Creating .env file..."
    cat > .env << EOF
# Database Configuration
DATABASE_URL=mysql+pymysql://${DB_USER}:${DB_PASSWORD}@127.0.0.1:3306/${DB_NAME}

# JWT Settings
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Marzban API (Live instance)
MARZBAN_API_BASE_URL=https://panel.abresani.com
MARZBAN_SUDO_USERNAME=${MARZBAN_USERNAME}
MARZBAN_SUDO_PASSWORD=${MARZBAN_PASSWORD}

# Zarinpal Payment Gateway
ZARINPAL_MERCHANT_ID=${ZARINPAL_MERCHANT_ID}
FRONTEND_URL=https://${DOMAIN_NAME}
ZARINPAL_CALLBACK_URL=https://${DOMAIN_NAME}/api/v1/payments/zarinpal/callback

# Initial Super Admin for this Panel
INITIAL_SUPER_ADMIN_USERNAME=superadmin
INITIAL_SUPER_ADMIN_EMAIL=superadmin@${DOMAIN_NAME}
INITIAL_SUPER_ADMIN_PASSWORD=${PANEL_SUPERADMIN_PASSWORD}
EOF

    echo "Backend setup complete."
}

setup_frontend() {
    _header "Setting up Frontend"
    cd "$PROJECT_DIR/frontend" || _error "Frontend directory not found."

    echo "Installing Node.js dependencies..."
    npm install || _error "Failed to install npm dependencies."

    echo "Creating .env.production file..."
    cat > .env.production << EOF
VUE_APP_API_BASE_URL=https://${DOMAIN_NAME}/api/v1
EOF

    echo "Building frontend for production..."
    npm run build || _error "Failed to build frontend."

    echo "Frontend setup complete."
}


setup_nginx() {
    _header "Setting up Nginx Reverse Proxy"

    # Create Nginx config from template
    NGINX_TEMPLATE_PATH="$PROJECT_DIR/nginx.conf.template"
    if [ ! -f "$NGINX_TEMPLATE_PATH" ]; then
        # As a fallback if the template file is not in the repo, create it.
        cat > "$NGINX_TEMPLATE_PATH" <<'EOF'
server {
    listen 80;
    server_name YOUR_DOMAIN_NAME;
    location / {
        return 301 https://$host$request_uri;
    }
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
}
server {
    listen 443 ssl http2;
    server_name YOUR_DOMAIN_NAME;
    # SSL certs will be added by Certbot
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    location / {
        root PROJECT_DIR/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
}
EOF
    fi

    FINAL_NGINX_CONF="/etc/nginx/sites-available/$NGINX_CONF_NAME"

    # Replace placeholders
    sed -e "s|YOUR_DOMAIN_NAME|$DOMAIN_NAME|g" -e "s|PROJECT_DIR|$PROJECT_DIR|g" "$NGINX_TEMPLATE_PATH" > "$FINAL_NGINX_CONF"

    # Enable the site
    ln -sfn "$FINAL_NGINX_CONF" "/etc/nginx/sites-enabled/$NGINX_CONF_NAME"

    # Remove default site if it exists
    rm -f /etc/nginx/sites-enabled/default

    echo "Testing Nginx configuration..."
    nginx -t || _error "Nginx configuration test failed."

    echo "Reloading Nginx..."
    systemctl reload nginx

    echo "Nginx setup complete. Now, let's get an SSL certificate."
    echo "Installing Certbot..."
    apt-get install -y certbot python3-certbot-nginx || _error "Failed to install Certbot."

    echo "Requesting SSL certificate from Let's Encrypt..."
    certbot --nginx -d "$DOMAIN_NAME" --non-interactive --agree-tos -m "admin@$DOMAIN_NAME" || _error "Certbot failed to obtain SSL certificate."

    echo "Reloading Nginx with SSL configuration..."
    systemctl reload nginx

    echo "SSL setup complete. Your site is now available at https://$DOMAIN_NAME"
}

setup_systemd_service() {
    _header "Setting up Systemd Service for Backend"

    # Create the systemd service file
    cat > "/etc/systemd/system/$SYSTEMD_SERVICE_NAME" << EOF
[Unit]
Description=VPN Admin Panel Gunicorn Service
After=network.target

[Service]
# Run as a non-root user for better security, e.g., 'www-data' or a dedicated user
# Ensure this user has ownership of the project directory
User=root
Group=www-data
WorkingDirectory=$PROJECT_DIR/backend
# ExecStart uses the full path to gunicorn inside the venv
ExecStart=$PROJECT_DIR/backend/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000 app.main:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    echo "Setting ownership of project directory..."
    chown -R root:www-data "$PROJECT_DIR"
    chmod -R 775 "$PROJECT_DIR"

    echo "Reloading systemd daemon..."
    systemctl daemon-reload

    echo "Enabling and starting the panel service..."
    systemctl enable "$SYSTEMD_SERVICE_NAME"
    systemctl start "$SYSTEMD_SERVICE_NAME"

    # Check status
    sleep 5
    systemctl status "$SYSTEMD_SERVICE_NAME" --no-pager

    echo "Systemd service setup complete."
}


# --- Main Execution ---
main() {
    check_root
    get_user_input
    clone_project
    check_dependencies
    setup_database
    setup_backend
    setup_frontend
    setup_nginx
    setup_systemd_service

    _header "Installation Complete!"
    echo "Your VPN Admin Panel is now running at: https://$DOMAIN_NAME"
    echo "Initial Super Admin username: superadmin"
    echo "Please use the password you provided during setup to log in."
}

# Run the main function
main
