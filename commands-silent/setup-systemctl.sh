#!/bin/bash

echo "sudo apt update" && sudo apt update -qq

# Uncomment the lines below if you want to echo commented lines as well
# echo "sudo nano /etc/nginx/sites-available/iberry"
# echo "sudo nano /etc/nginx/sites-available/iberry"

echo "sudo systemctl start docker" && sudo systemctl start docker
echo "sudo systemctl enable docker" && sudo systemctl enable docker

echo "sudo cp -f commands-silent/docker-compose-app.service /etc/systemd/system/" && sudo cp -f commands-silent/docker-compose-app.service /etc/systemd/system/

# Uncomment the lines below if you want to echo commented lines as well
# echo "sudo nano /etc/systemd/system/docker-compose-app.service"
# echo "sudo nano /etc/systemd/system/docker-compose-app.service"

echo "sudo systemctl daemon-reload" && sudo systemctl daemon-reload
echo "sudo systemctl enable docker-compose-app" && sudo systemctl enable docker-compose-app

# Uncomment the line below if you want to echo commented lines as well
# echo "sudo systemctl start docker-compose-app"
sudo systemctl start --no-block docker-compose-app
