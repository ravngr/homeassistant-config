#!/bin/bash
# shellcheck disable=SC2199,SC2076

## Globals
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
REPO_DIR=$(readlink -f "${SCRIPT_DIR}/..")
CONFIG_DIR=$(readlink -f "${REPO_DIR}/config")


# Scan configuration files for secrets
declare -a secrets=()

while IFS= read -r -d '' file; do
    readarray -t file_secrets < <(sed -rn "s/^.*\!secret (.*)$/\1/p" "$file")

    if [ ${#file_secrets[@]} -gt 0 ]; then
        # echo "$file"
        # printf "  %s\n" "${file_secrets[@]}"
        secrets+=("${file_secrets[@]}")
    fi
done < <(find "${CONFIG_DIR}" -type f -name "*.yaml" -print0)

# Sort secrets
mapfile -t secrets < <(echo "${secrets[@]}" | tr ' ' '\n' | sort -u | awk 'NF > 0 {print $0}')

if [ ${#secrets[@]} -eq 0 ]; then
    exit 0
fi

# echo "Required secrets"
# printf "  - %s\n" "${secrets[@]}"


# Scan secrets.ci.yaml
ci_secrets=$(sed -rn "s/^([a-z_0-9]*):.*$/\1/p" "${CONFIG_DIR}/secrets.ci.yaml")
mapfile -t ci_secrets < <(echo "${ci_secrets[@]}" | tr ' ' '\n' | sort -u | awk 'NF > 0 {print $0}')


missing=false

for secret in "${secrets[@]}"; do
    if [[ ! " ${ci_secrets[@]} " =~ " ${secret} " ]]; then
        missing=true
        echo "ERROR: $secret missing from secrets.ci.yaml"
    fi
done


# Repeat for secrets.yaml if present
if [ -f "${CONFIG_DIR}/secrets.yaml" ]; then
    external_secrets=$(sed -rn "s/^([a-z_0-9]*):.*$/\1/p" "${CONFIG_DIR}/secrets.ci.yaml")
    mapfile -t external_secrets < <(echo "${external_secrets[@]}" | tr ' ' '\n' | sort -u | awk 'NF > 0 {print $0}')

    for secret in "${secrets[@]}"; do
        if [[ ! " ${external_secrets[@]} " =~ " ${secret} " ]]; then
            missing=true
            echo "ERROR: $secret missing from secrets.yaml"
        fi
    done
fi

if $missing; then
    exit 1
else
    exit 0
fi
