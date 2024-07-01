#!/usr/bin/env bash

# set -x

# Default options to truncate output
dig_options=("+stats" "+nocmd" "+nocomments" "+noquestion" "+time=2" "+tries=1" "+fail")

if [ "$#" -lt 3 ]; then
    echo "Usage: $0 <domain> <record_type> <server or '-'> [options, ...]"
    exit 1
fi

domain="${1}"
shift
record_type="${1}"
shift
server="${1}"
shift

options=("${dig_options[@]}" "$@")

if [ "${server}" = "-" ]; then
    command=("dig")
else
    command=("dig" "@${server}")
fi

dig_output=$("${command[@]}" \
    "${domain}" \
    "${record_type}" \
    "${options[@]}" \
)

if [[ $? -ne 0 ]]; then
    echo "unavailable"
    exit 1
fi

# Check if record name is in output (record found)
if echo "${dig_output}" | egrep -q "^${domain//./\\.}\."; then
    echo "${dig_output}" | awk '/Query time:/ {print $4}'
else
    echo "unknown"
    exit 1
fi
