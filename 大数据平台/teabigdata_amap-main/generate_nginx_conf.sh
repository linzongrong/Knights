#!/bin/bash

# Check if the environment variable is set
if [ -z "$AMAP_SECURITY_CODE" ]; then
    echo "Error: AMAP_SECURITY_CODE environment variable is not set."
    echo "Usage: export AMAP_SECURITY_CODE=your_code_here && ./generate_nginx_conf.sh"
    exit 1
fi

# Use envsubst to replace ONLY the specified variable, preserving Nginx's $args, $uri, etc.
# We explicitly pass '$AMAP_SECURITY_CODE' to envsubst so it doesn't touch other $vars.
export AMAP_SECURITY_CODE
envsubst '$AMAP_SECURITY_CODE' < nginx.conf.template > nginx.conf

echo "Successfully generated nginx.conf with security code."
