#!/bin/sh

response=$(curl -w "%{json}" -o /dev/null -sL "$@")

if [ $? -eq 0 ]; then
    echo "${response}"
else
    echo "unknown"
fi
