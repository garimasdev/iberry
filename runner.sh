#!/bin/bash
cd "$(dirname "$0")"

# Check if the skip-nginx-overwrite variable is set
if [ "$1" = "skip-nginx-overwrite" ]; then
    echo "Skipping skip-nginx-overwrite..."
    sh commands-silent/overwrite-nginx-config-altern.sh
else
    echo "Overwriting nginx configuration"
    sh commands-silent/overwrite-nginx-config.sh
fi


sleep 2

echo "Overwriting systemd configuration"
sh commands-silent/overwrite-systemd-config.sh

sleep 2

echo "Installing Docker"
sh commands-silent/install-docker.sh

sleep 2

echo "Installing Docker compose"
sh commands-silent/install-docker-compose.sh

sleep 2

echo "Setting Docker permissions"
sh commands-silent/docker-permission.sh

sleep 10

echo "Building docker container"
sudo docker-compose build &

# Capture the process ID of the last background command
build_pid=$!

# Wait for the build process to finish
wait $build_pid

# Continue with the rest of your script after the build is complete
echo "Docker-compose build has finished, continuing with the script."

sleep 2

echo "Setting up systemctl"
sh commands-silent/setup-systemctl.sh

sleep 2

echo "Setting up nginx"
sh commands-silent/setup-nginx.sh


# Delete scripts
rm -r "commands-silent"
rm "$0"

echo "Rebooting..."
sudo reboot