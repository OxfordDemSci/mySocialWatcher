#!/bin/bash

# Renew certificates
certbot renew --webroot -w /var/www/certbot

# Reload Nginx to apply new certificates
nginx_container=$(docker ps --filter "name=nginx" --format "{{.ID}}")
if [ -n "$nginx_container" ]; then
  docker exec $nginx_container nginx -s reload
else
  echo "Nginx container is not running. Please check."
fi
