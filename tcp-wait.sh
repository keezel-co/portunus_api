#!/bin/sh

host=$1
port=$2

echo "Waiting ${host} to launch on ${port}..."

while ! nc -z ${host} ${port}; do   
  sleep 1
done

echo "OK"
shift 2
$*
