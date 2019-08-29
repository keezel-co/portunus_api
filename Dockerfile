FROM python:3.7-alpine

RUN apk update && apk add --no-cache postgresql-dev mariadb-dev gcc python3-dev musl-dev libffi-dev linux-headers openssl wireguard-tools-wg make
COPY requirements.txt /root
RUN pip install -r /root/requirements.txt

RUN adduser -Dh /wgpt wgpt
WORKDIR /wgpt

COPY wgpt.py create_database.py tcp-wait.sh entrypoint.sh certgen-entrypoint.sh /wgpt/

RUN mkdir /wgpt/wgpt
COPY wgpt/ /wgpt/wgpt

CMD ["/wgpt/entrypoint.sh"]
