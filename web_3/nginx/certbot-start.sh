#!/bin/sh

DOMAIN="web3.pucavv.io.vn"
EMAIL="admin@pucavv.io.vn"

if ! certbot certificates | grep -q "Domains: $DOMAIN"; then
    echo "Obtaining new certificate for $DOMAIN"
    certbot --nginx -d "$DOMAIN" --redirect --agree-tos --no-eff-email --email "$EMAIL" --force-renewal || true
fi

exec nginx -g 'daemon off;'