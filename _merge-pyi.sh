#!/bin/bash

#
# Copyright (c) 2024.
# Creative Commons 4 for original code
# GPL3 for rewrite
#

MERGE_PYI='.venv/bin/merge-pyi -i'
MERGE_PYI='.venv/bin/merge-pyi --diff'
for p in oewn_core oewn_xml tests; do
    while read -r f; do
      b=$(basename "$f");
      s="${b%.*}";
      d=$(dirname "$f");
      echo "$d/$s";
      $MERGE_PYI  "$d/$s.py" ".pytype/pyi/$d/$s.pyi"; done < \
    <(find $p -name '*.py')
done