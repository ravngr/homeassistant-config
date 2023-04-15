#!/bin/bash

function array_diff {
    local -n a=$1
    local -n b=$2
    local result=()

    for i in "${a[@]}"; do
        if [[ ! " ${b[*]} " =~ " $i " ]]; then
            result+=("$i")
        fi
    done

    echo "${result[@]}"
}


config_secrets=()

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
CONFIG_DIR="${SCRIPT_DIR}/../config"

# Scan configuration
for file in $(find "${CONFIG_DIR}" -type f -name "*.yaml"); do
    config_secrets+=( $(sed -rn "s/^.*\!secret (.*)$/\1/p" "${file}") )
done

# Scan secrets file
secrets_secrets=$(sed -rn "s/^([a-z_0-9]*):.*$/\1/p" "${CONFIG_DIR}/secrets.yaml")

# Scan secrets CI file
ci_secrets=$(sed -rn "s/^([a-z_0-9]*):.*$/\1/p" "${CONFIG_DIR}/secrets.ci.yaml")

# Sort secrets
config_secrets=( $(printf '%s\n' "${config_secrets[@]}" | sort -u) )
secrets_secrets=( $(printf '%s\n' "${secrets_secrets[@]}" | sort -u) )
ci_secrets=( $(printf '%s\n' "${ci_secrets[@]}" | sort -u) )

# Get diff
diff=$( array_diff config_secrets secrets_secrets )
echo "Missing from secrets.yaml"
printf '  %s\n' "${diff[@]}"

diff=$( array_diff config_secrets ci_secrets )
echo "Missing from secrets.ci.yaml"
printf '  %s\n' "${diff[@]}"

diff=$( array_diff secrets_secrets config_secrets )
echo "Unused in secrets.yaml"
printf '  %s\n' "${diff[@]}"

diff=$( array_diff ci_secrets config_secrets )
echo "Unused in secrets.ci.yaml"
printf '  %s\n' "${diff[@]}"
