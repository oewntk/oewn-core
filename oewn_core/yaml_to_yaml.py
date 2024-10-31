#!/usr/bin/python3

"""
WordNet load-save
Will have a normalizing effect, after which it's not modified

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
from oewn_core.wordnet_toyaml import save


def main() -> None:
    """
    WordNet load-save
    Will have a normalizing effect, after which it's not modified
    """
    arg_parser = argparse.ArgumentParser(description="load from yaml and save")
    arg_parser.add_argument('in_dir', type=str, help='from-dir')
    arg_parser.add_argument('out_dir', type=str, help='to-dir')
    args = arg_parser.parse_args()

    wn = load(args.in_dir)
    save(wn, args.out_dir)


if __name__ == '__main__':
    start_time = time.time()
    main()
    end_time = time.time()
    duration = end_time - start_time
    print(f"Identity conversion took {duration:.6f} seconds", file=sys.stderr)
