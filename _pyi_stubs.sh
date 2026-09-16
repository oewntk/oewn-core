#!/bin/bash

#
# Copyright (c) 2024-2026.
# Creative Commons 4 for original code
# GPL3 for rewrite
#

./.venv/bin/pytype --pythonpath=. -o .pytype_gen/ oewn_core oewn_plus oewn_xml oewn_syntagnet oewn_validate
