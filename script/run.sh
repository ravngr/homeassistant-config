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


## Create temporary storage
export_path=$(mktemp -d -t test_export.XXXXXXXX)

print_info "Using temporary export directory $(print_style "${export_path}" "${TERM_STYLE_BOLD}")"

cleanup() {
    print_info "Cleaning up temporary data directory $(print_style "${export_path}" "${TERM_STYLE_BOLD}")"
    rm -Rf "${export_path}"
}

trap cleanup EXIT

"${SCRIPT_PATH}/config_export.sh" "${export_path}"

# Remove optional packages
grep -Rl "run::remove" "${export_path}" | xargs rm -f

# Use SQLite DB during run
sed -ie 's/^recorder_db_url: .*$/recorder_db_url: "sqlite:\/\/\/\/config\/home-assistant_v2.db"/g' "${export_path}/secrets.yaml"

docker run \
    --name homeassistant_config \
    --rm \
    -v "${export_path}:/config" \
    -v "${REPO_PATH}/staging/.storage:/config/.storage" \
    -p "18123:8123/tcp" \
    -e "TZ=${TZ}" \
    "ghcr.io/home-assistant/home-assistant:stable" \
    python -m homeassistant --config "/config"
