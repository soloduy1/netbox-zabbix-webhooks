FROM almir/webhook:latest

ENV NETBOX_URL="${NETBOX_URL}"
ENV NETBOX_TOKEN="${NETBOX_TOKEN}"
ENV ZABBIX_URL="${ZABBIX_URL}"
ENV ZABBIX_TOKEN="${ZABBIX_TOKEN}"
ENV ROLES="${ROLES}"
ENV TEMPLATES="${TEMPLATES}"
ENV TEMPLATE_DEFAULT="${TEMPLATE_DEFAULT}"
ENV INTERFACE_REGEX="${INTERFACE_REGEX}"
ENV TG_TOKEN="${TG_TOKEN}"
ENV TG_CHATID="${TG_CHATID}"

RUN apk add --no-cache \
    build-base \
    libffi-dev \
    openssl-dev \
    zlib-dev \
    wget \
    tar \
    xz \
    bash

RUN wget https://www.python.org/ftp/python/3.10.0/Python-3.10.0.tar.xz \
    && tar -xf Python-3.10.0.tar.xz \
    && cd Python-3.10.0 \
    && ./configure --enable-optimizations \
    && make -j$(nproc) \
    && make install \
    && cd .. \
    && rm -rf Python-3.10.0 Python-3.10.0.tar.xz

COPY hooks.json /etc/webhook/hooks.json
COPY service /etc/webhook

COPY certs/root.crt /usr/local/share/ca-certificates/root.crt
COPY certs/intermed.crt /usr/local/share/ca-certificates/intermed.crt
COPY certs/cert.crt /usr/local/share/ca-certificates/cert.crt

RUN cat /usr/local/share/ca-certificates/root.crt >> /etc/ssl/cert.pem
RUN cat /usr/local/share/ca-certificates/intermed.crt >> /etc/ssl/cert.pem
RUN cat /usr/local/share/ca-certificates/cert.crt >> /etc/ssl/cert.pem

RUN apk update
RUN python3.10 -m pip install --upgrade pip setuptools wheel
RUN python3.10 -m pip install ansible

RUN ansible-galaxy collection install community.general
RUN ansible-galaxy collection install community.zabbix

RUN pip3 install pyzabbix zabbix-api pynetbox emoji pyTelegramBotAPI certifi
RUN pip3 config set global.cert /etc/ssl/certs/ca-certificates.crt
