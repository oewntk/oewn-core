#!/bin/bash

#
# Copyright (c) 2024.
# Creative Commons 4 for original code
# GPL3 for rewrite
#

MEM=-Xmx2G

R='\u001b[31m'
G='\u001b[32m'
Y='\u001b[33m'
B='\u001b[34m'
M='\u001b[35m'
C='\u001b[36m'
Z='\u001b[0m'

DATA="$1"
shift # consume

XSD="1.3/WN-LMF-1.3.xsd"
echo -e "${M}XSD: $XSD${Z}" 1>&2;
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
XSD="${DIR}/${XSD}"

java -jar "${DIR}/validator2-uber.jar" "$XSD" "${DATA}" "$@"
