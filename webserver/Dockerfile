FROM nginx:alpine

RUN apk update && apk add --no-cache apache2-utils

COPY run.sh /run.sh
COPY nginx.conf /nginx.conf
COPY www/ /var/www

#RUN sed -i "s/CERT_SSL_CHAIN/${CERT_SSL_CHAIN}"/g /etc/nginx/conf.d/default.conf
#RUN sed -i "s/CERT_SSL_SERVER_KEY/${CERT_SSL_SERVER_KEY}"/g /etc/nginx/conf.d/default.conf
#RUN sed -i "s/CERT_SSL_CA/${CERT_SSL_CA}"/g /etc/nginx/conf.d/default.conf

CMD ["/run.sh"]
