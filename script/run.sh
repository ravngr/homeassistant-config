#!/bin/bash

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ROOT_DIR="${SCRIPT_DIR}/.."

# rm -R "${ROOT_DIR}/build"
mkdir "${ROOT_DIR}/build"
cp -R "${ROOT_DIR}/config" "${ROOT_DIR}/build"

# Use SQLite DB
sed -ie 's/^recorder_db_url: .*$/recorder_db_url: "sqlite:\/\/\/\/config\/home-assistant_v2.db"/g' "${ROOT_DIR}/build/config/secrets.yaml"

# Remove optional packages
grep -Rl "run::remove" "${ROOT_DIR}/build/config" | xargs rm -f

# Fix permissions
chown -R root:root "${ROOT_DIR}/build/config/ssh"
find "${ROOT_DIR}/build/config/ssh" -type d -exec chmod 700 {} +
find "${ROOT_DIR}/build/config/ssh" -type f -exec chmod 600 {} +

docker run \
    --name homeassistant_config \
    --rm \
    -v "${ROOT_DIR}/build/config:/config" \
    -p "18123:8123/tcp" \
    -e "TZ=${TZ}" \
    "ghcr.io/home-assistant/home-assistant:stable" \
    python -m homeassistant --config "/config"
