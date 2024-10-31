#!/usr/bin/python3

"""
WordNet load from XML-save to YAML
Will have a normalizing effect, after which it's idempotent

Author: John McCrae <john@mccr.ae> for original code
Author: Bernard Bou <1313ou@gmail.com> for rewrite and revamp
"""

#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import argparse
import sys
import time

from oewn_core.wordnet_toyaml import save
from oewn_xml.wordnet_fromxml import load


def xml1_to_yaml(in_file, out_dir) -> None:
    wn = load(in_file)
    save(wn, out_dir)


def main() -> None:
    arg_parser = argparse.ArgumentParser(description="load from xml and save to yaml")
    arg_parser.add_argument('in_file', type=str, help='from-file')
    arg_parser.add_argument('out_dir', type=str, help='to-dir')
    args = arg_parser.parse_args()
    xml1_to_yaml(args.in_file, args.out_dir)


if __name__ == '__main__':
    start_time = time.time()
    main()
    end_time = time.time()
    duration = end_time - start_time
    print(f"XML-YAML conversion took {duration:.6f} seconds", file=sys.stderr)
