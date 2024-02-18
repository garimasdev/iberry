#!/bin/bash



# Specify the file path and name
nginx_config_file="commands-silent/docker-compose-app.service"
current_location="$(pwd)"


# Nginx configuration content with user-provided IP
nginx_config="
[Unit]
Description=Docker Compose Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=true
ExecStart=/usr/local/bin/docker-compose -f $current_location/docker-compose.yml up
ExecStop=/usr/local/bin/docker-compose -f $current_location/docker-compose.yml down

[Install]
WantedBy=default.target
"

# Write the configuration to the file (replace the existing file)
echo "$nginx_config" | sudo tee "$nginx_config_file" > /dev/null

# Optionally, display a message indicating success
echo "Nginx configuration file created successfully at: $nginx_config_file"
