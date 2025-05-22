docker run --rm \
    -v $(pwd)/certbot-etc:/etc/letsencrypt \
    -v $(pwd)/html:/var/www/certbot \
    certbot/certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --agree-tos \
    --no-eff-email \
    --email daniel.valdenegro@demography.ox.ac.uk \
    -d digitrace-datahub.ndph.ox.ac.uk  \
    -d www.digitrace-datahub.ndph.ox.ac.uk
