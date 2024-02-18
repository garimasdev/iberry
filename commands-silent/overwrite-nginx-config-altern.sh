#!/bin/bash


# Specify the file path and name
nginx_config_file="commands-silent/iberry"
current_location="$(pwd)"

# Nginx configuration content with user-provided IP
nginx_config="

    location /static/ {
        alias $current_location/static/;
    }

    location /media/ {
        alias $current_location/media/;
    }
}
"

# Use sed to replace lines 10 and onwards with the new configuration
sed -i '11,$d' "$nginx_config_file"  # Delete lines 10 to the end
echo "$nginx_config" | sudo tee -a "$nginx_config_file" > /dev/null  # Append the new configuration

# Optionally, display a message indicating success
echo "Nginx configuration file updated successfully at: $nginx_config_file"
