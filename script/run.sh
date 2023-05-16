#!/bin/bash

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

## Globals/imports
SCRIPT_PATH=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
export SCRIPT_PATH

REPO_PATH=$(readlink -f "${SCRIPT_PATH}/..")
export REPO_PATH

. "${REPO_PATH}/deps/bashplate/bashplate.sh"

build_path="${REPO_PATH}/build"

mkdir -p "${build_path}"

"${SCRIPT_DIR}/config_export.sh" "${build_path}"

# Use SQLite DB
sed -ie 's/^recorder_db_url: .*$/recorder_db_url: "sqlite:\/\/\/\/config\/home-assistant_v2.db"/g' "${build_path}/secrets.yaml"

# Remove optional packages
grep -Rl "run::remove" "${build_path}" | xargs rm -f

docker run \
    --name homeassistant_config \
    --rm \
    -v "${build_path}:/config" \
    -p "18123:8123/tcp" \
    -e "TZ=${TZ}" \
    "ghcr.io/home-assistant/home-assistant:stable" \
    python -m homeassistant --config "/config"
