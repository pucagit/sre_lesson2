#!/bin/sh

DOMAIN="web3.pucavv.io.vn"
EMAIL="admin@pucavv.io.vn"

# Check if the certificate already exists, if not, obtain a new one
if ! certbot certificates | grep -q "Domains: $DOMAIN"; then
    echo "Obtaining new certificate for $DOMAIN"
    certbot --nginx -d "$DOMAIN" --redirect --agree-tos --no-eff-email --email "$EMAIL" --force-renewal || true
fi

# Start nginx in the foreground
exec nginx -g 'daemon off;'