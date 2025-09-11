#!/bin/sh
set -eu

DOMAIN="web1.pucavv.io.vn"
EMAIL="admin@pucavv.io.vn"

certbot certificates >/dev/null 2>&1 || true

if ! certbot certificates | grep -q "Domains: $DOMAIN"; then
    certbot --nginx -d "$DOMAIN" --redirect --agree-tos --no-eff-email --email "$EMAIL" || true
fi

(
    while true; do
        sleep 12h
        certbot renew --nginx --quiet --deploy-hook "nginx -s reload" | true
    done
) &

exec nginx -g 'daemon off;'