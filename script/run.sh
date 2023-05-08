#!/bin/bash

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
BUILD_DIR=$(readlink -f "${SCRIPT_DIR}/../build")

mkdir -p "${BUILD_DIR}"

${SCRIPT_DIR}/config_export.sh "${BUILD_DIR}"

# Use SQLite DB
sed -ie 's/^recorder_db_url: .*$/recorder_db_url: "sqlite:\/\/\/\/config\/home-assistant_v2.db"/g' "${BUILD_DIR}/secrets.yaml"

# Remove optional packages
grep -Rl "run::remove" "${BUILD_DIR}" | xargs rm -f

docker run \
    --name homeassistant_config \
    --rm \
    -v "${BUILD_DIR}:/config" \
    -p "18123:8123/tcp" \
    -e "TZ=${TZ}" \
    "ghcr.io/home-assistant/home-assistant:stable" \
    python -m homeassistant --config "/config"
