#!/usr/bin/python3

"""
WordNet load from YAML-save to XML

Author: John McCrae <john@mccr.ae> for original code
Author: Bernard Bou <1313ou@gmail.com> for rewrite and revamp
"""

#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import argparse
import sys
import time

from oewn_core.wordnet_fromyaml import load
from oewn_xml.wordnet_toxml import save


def yaml_to_xml1(in_dir, out_file) -> None:
    wn = load(in_dir)
    save(wn, out_file)


def main() -> None:
    arg_parser = argparse.ArgumentParser(description="load from yaml and save")
    arg_parser.add_argument('in_dir', type=str, help='from-dir')
    arg_parser.add_argument('out_file', type=str, help='to-file')
    args = arg_parser.parse_args()
    yaml_to_xml1(args.in_dir, args.out_file)


if __name__ == '__main__':
    start_time = time.time()
    main()
    end_time = time.time()
    duration = end_time - start_time
    print(f"YAML-XML conversion took {duration:.6f} seconds", file=sys.stderr)
