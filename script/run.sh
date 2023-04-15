#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ROOT_DIR="${SCRIPT_DIR}/.."

sudo rm -R "${ROOT_DIR}/build" 
mkdir "${ROOT_DIR}/build"
cp -R "${ROOT_DIR}/config" "${ROOT_DIR}/build"
sed -ie 's/^recorder_db_url: .*$/recorder_db_url: "sqlite:\/\/\/\/config\/home-assistant_v2.db"/g' "${ROOT_DIR}/build/config/secrets.yaml"

docker run \
    --rm \
    -v "${ROOT_DIR}/build/config:/config" \
    -p "18123:8123/tcp" \
    -e "TZ=${TZ}" \
    "ghcr.io/home-assistant/home-assistant:stable" \
    python -m homeassistant --config "/config"
