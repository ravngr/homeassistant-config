#!/bin/bash

## Globals
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
RESET='\033[0m'

# Locate script directory
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
REPO_DIR=$(readlink -f "${SCRIPT_DIR}/..")
CONFIG_DIR=$(readlink -f "${REPO_DIR}/config")


## Arguments
# Check for required arguments
if [ $# -lt 1 ]; then
    echo "Usage: $0 <export path>"
    exit 1
fi

export_path="$1"
shift 1


## Export configuration
# Copy files but do not overwrite (preserve UI defined entities)
for file in "automations.yaml" "scenes.yaml" "scripts.yaml"; do
    if [ ! -e "${export_path}/${file}" ]; then
        printf "${YELLOW}Using default ${file}${RESET}\n"
        cp "${CONFIG_DIR}/${file}" "${export_path}/${file}"
    fi
done

# Cleanup old packages and SSH configs
printf "${GREEN}Removing old files${RESET}\n"
rm -Rf "${export_path}/packages"
rm -f "${export_path}/ssh/config*"

# Copy configuration core files
printf "${GREEN}Copying configuration.yaml${RESET}\n"
cp "${CONFIG_DIR}/configuration.yaml" "${export_path}"
printf "${GREEN}Copying secrets.yaml${RESET}\n"
cp "${CONFIG_DIR}/secrets.yaml" "${export_path}"

# Copy directories
find "${CONFIG_DIR}" -maxdepth 1 -type d -print0 | while read -d $'\0' dir; do
    printf "${GREEN}Copying directory $dir${RESET}\n"
    cp -R "$dir" "${export_path}"
done

# Fix permissions on SSH files
printf "${GREEN}Fixing SSH file permissions${RESET}\n"
chown -R root:root "${export_path}/ssh"
find "${export_path}/ssh" -type d -exec chmod 700 {} +
find "${export_path}/ssh" -type f -exec chmod 600 {} +
