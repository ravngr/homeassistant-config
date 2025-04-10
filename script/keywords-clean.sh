#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail

sed -e 's/\$GitAuthor[^$]*\$/\$GitAuthor\$/g' \
    -e 's/\$GitHash[^$]*\$/\$GitHash\$/g' \
    -e 's/\$GitDate[^$]*\$/\$GitDate\$/g'
