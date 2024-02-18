#!/bin/bash

echo "sudo apt update" && sudo apt update -qq

echo "sudo apt install nginx" && sudo apt install -y -qq nginx

echo "sudo cp -f commands-silent/iberry /etc/nginx/sites-available/" && sudo cp -f commands-silent/iberry /etc/nginx/sites-available/

sudo ln -s /etc/nginx/sites-available/iberry /etc/nginx/sites-enabled
sudo rm /etc/nginx/sites-enabled/default
echo "sudo systemctl restart nginx" && sudo systemctl restart nginx

