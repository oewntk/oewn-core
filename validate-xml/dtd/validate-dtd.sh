#
# Copyright (c) 2024.
# Creative Commons 4 for original code
# GPL3 for rewrite
#

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
xmllint --noout --dtdvalid "${DIR}/WN-LMF-1.3-collocation.dtd" "$1"
