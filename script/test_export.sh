#!/bin/bash

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
