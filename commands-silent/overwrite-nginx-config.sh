#!/bin/bash

# Prompt user for the server IP address
read -p "Enter the domain or server IP address: " server_ip

# Specify the file path and name
nginx_config_file="commands-silent/iberry"
current_location="$(pwd)"

# Nginx configuration content with user-provided IP
nginx_config="
server {
    listen 80;
    server_name $server_ip;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }

    location /static/ {
        alias $current_location/static/;
    }

    location /media/ {
        alias $current_location/media/;
    }
}
"

# Write the configuration to the file (replace the existing file)
echo "$nginx_config" | sudo tee "$nginx_config_file" > /dev/null

# Optionally, display a message indicating success
echo "Nginx configuration file created successfully at: $nginx_config_file"
