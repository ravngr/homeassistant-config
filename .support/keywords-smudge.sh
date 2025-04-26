#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail

if [ -z "$1" ]; then
    echo "Usage: $0 <file>"
    exit 1
fi

file="${1}"

# Check file exists
if [ ! -f "${file}" ]; then
    echo "Error: '${file}' not found."
    exit 1
fi

# Get last commit info for the file
git_author=$(git log -1 --format='%an' -- "${file}")
git_hash=$(git log -1 --format='%h' -- "${file}")
git_date=$(git log -1 --format='%ad' -- "${file}")

# Sanity check
if [ -z "${git_author}" ] || [ -z "${git_hash}" ] || [ -z "${git_date}" ]; then
    echo "Error: Could not retrieve Git info for '${file}'."
    exit 1
fi

sed -e "s/\\\$GitAuthor\\\$/\\\$GitAuthor ${git_author}\\\$/g" \
    -e "s/\\\$GitHash\\\$/\\\$GitHash ${git_hash}\\\$/g" \
    -e "s/\\\$GitDate\\\$/\\\$GitDate ${git_date}\\\$/g"
