FROM nginx:1.29.1-alpine-slim

RUN rm -f /etc/nginx/conf.d/*

RUN apk add --no-cache certbot certbot-nginx 

COPY nginx.conf /etc/nginx/nginx.conf
COPY certbot-start.sh /usr/local/bin/certbot-start.sh

RUN chmod +x /usr/local/bin/certbot-start.sh
ENTRYPOINT ["/usr/local/bin/certbot-start.sh"]