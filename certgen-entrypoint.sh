#!/bin/sh

if [ -z "$CERT_SSL_CA" ]
then
  echo Missing CERT_SSL_CA
  exit 1
fi

if [ -z "$CERT_SSL_CA_KEY" ]
then
  echo Missing $CERT_SSL_CA_KEY
  exit 1
fi

if [ -z "$CERT_SSL_SERVER" ]
then
  echo Missing $CERT_SSL_SERVER
  exit 1
fi

if [ -z "$CERT_SSL_SERVER_KEY" ]
then
  echo Missing $CERT_SSL_SERVER_KEY
  exit 1
fi

if [ -z "$CERT_SSL_CHAIN" ]
then
  echo Missing $CERT_SSL_CHAIN
  exit 1
fi

if
  [ ! -e "$CERT_SSL_CA" ] ||
  [ ! -e "$CERT_SSL_CA_KEY" ] ||
  [ ! -e "$CERT_SSL_SERVER" ] ||
  [ ! -e "$CERT_SSL_SERVER_KEY" ] ||
  [ ! -e "$CERT_SSL_CHAIN" ]
then
    echo Generating CA certificate

    openssl genrsa -out "${CERT_SSL_CA_KEY}" 4096
    openssl req -x509 -new -key "${CERT_SSL_CA_KEY}" -out "${CERT_SSL_CA}" -days 36500 -subj "/CN=WGPT-CA-cert"

    openssl genrsa -out "${CERT_SSL_SERVER_KEY}" 4096
    openssl req -new -nodes \
      -key "${CERT_SSL_SERVER_KEY}" \
      -subj "/CN=*.wgpt" \
      -out "${CERT_SSL_SERVER}.csr"

    openssl x509 -req \
      -in "${CERT_SSL_SERVER}.csr" \
      -CA "${CERT_SSL_CA}" \
      -CAkey "${CERT_SSL_CA_KEY}" \
      -CAcreateserial \
      -out "${CERT_SSL_SERVER}" \
      -days 36500

    cat "$CERT_SSL_SERVER" "$CERT_SSL_CA" > "$CERT_SSL_CHAIN"
    rm "${CERT_SSL_SERVER}.csr"
else
    echo "Cert files present"
    ls -alh "$CERT_SSL_CA" "$CERT_SSL_CA_KEY" "$CERT_SSL_SERVER" "$CERT_SSL_SERVER_KEY" "$CERT_SSL_CHAIN"
fi

/wgpt/entrypoint.sh
