#!/bin/bash
# shellcheck disable=SC2199,SC2076

## Globals/imports
SCRIPT_PATH=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
export SCRIPT_PATH

REPO_PATH=$(readlink -f "${SCRIPT_PATH}/..")
export REPO_PATH

. "${REPO_PATH}/deps/bashplate/bashplate.sh"


## Scan secrets
# Locate config directory
config_path="${REPO_PATH}/config"

# Array for required secrets
declare -a secrets=()

# Missing secret flag
missing=false

# Scan configuration for use of !secret <name>
while IFS= read -r -d '' file; do
    print_debug "Scanning $(print_style "${file}" ${TERM_STYLE_BOLD})"
    readarray -t file_secrets < <(sed -rn "s/^.*\!secret (.*)$/\1/p" "$file")

    if [ ${#file_secrets[@]} -gt 0 ]; then
        for name in "${file_secrets[@]}"; do
            print_debug "> Secret $(print_style "${name}" ${TERM_STYLE_BOLD})"
        done

        secrets+=("${file_secrets[@]}")
    fi
done < <(find "${config_path}" -type f -name "*.yaml" -print0)

# Sort secrets
mapfile -t secrets < <(echo "${secrets[@]}" | tr ' ' '\n' | sort -u | awk 'NF > 0 {print $0}')

if [ ${#secrets[@]} -eq 0 ]; then
    exit 0
fi


# Scan secrets.ci.yaml
ci_secrets=$(sed -rn "s/^([a-z_0-9]*):.*$/\1/p" "${config_path}/secrets.ci.yaml")
mapfile -t ci_secrets < <(echo "${ci_secrets[@]}" | tr ' ' '\n' | sort -u | awk 'NF > 0 {print $0}')

for secret in "${secrets[@]}"; do
    if [[ ! " ${ci_secrets[@]} " =~ " ${secret} " ]]; then
        missing=true
        print_error "Missing secret $(print_style "${secret}" ${TERM_STYLE_BOLD}) from secrets.ci.yaml"
    fi
done


# Repeat for secrets.yaml if present
if [ -f "${config_path}/secrets.yaml" ]; then
    external_secrets=$(sed -rn "s/^([a-z_0-9]*):.*$/\1/p" "${config_path}/secrets.ci.yaml")
    mapfile -t external_secrets < <(echo "${external_secrets[@]}" | tr ' ' '\n' | sort -u | awk 'NF > 0 {print $0}')

    for secret in "${secrets[@]}"; do
        if [[ ! " ${external_secrets[@]} " =~ " ${secret} " ]]; then
            missing=true
            print_error "Missing secret $(print_style "${secret}" ${TERM_STYLE_BOLD}) from secrets.yaml"
        fi
    done
fi

if $missing; then
    exit 1
else
    exit 0
fi
