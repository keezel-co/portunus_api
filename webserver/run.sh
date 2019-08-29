#!/bin/sh

host=$1
port=$2

echo "Waiting certificates to be generated..."

while
  [ ! -e "$CERT_SSL_CA" ] ||
  [ ! -e "$CERT_SSL_SERVER_KEY" ] ||
  [ ! -e "$CERT_SSL_CHAIN" ]
do   
  sleep 1
done

echo "OK"

if
  [ ! -z "$HTTP_USER" ] &&
  [ ! -z "$HTTP_PASSWORD" ]
then
  AUTH_BASIC='auth_basic "Restricted access";'
  AUTH_BASIC_USER_FILE='auth_basic_user_file /etc/nginx/htpasswd;'
  rm -f /etc/nginx/htpasswd
  htpasswd -b -c /etc/nginx/htpasswd "${HTTP_USER}" "${HTTP_PASSWORD}"
else
  unset AUTH_BASIC
  unset AUTH_BASIC_USER_FILE
fi

export AUTH_BASIC
export AUTH_BASIC_USER_FILE
export uri='$uri'
envsubst < /nginx.conf > /etc/nginx/conf.d/default.conf

#cat /etc/nginx/conf.d/default.conf

/usr/sbin/nginx -g "daemon off;"
