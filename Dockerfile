FROM python:3.10.7-slim-bullseye

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN set -ex; \
    apt-get update; \
    apt-get install -y locales; \
    echo "ru_RU.UTF-8 UTF-8" >> /etc/locale.gen; \
    locale-gen; \
    pip install -U pip; \
    pip install --no-cache-dir -r requirements.txt; \
    rm -rf /var/lib/apt/lists/*
COPY . .
ENTRYPOINT /usr/src/app/docker-entrypoint.sh