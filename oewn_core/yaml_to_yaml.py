#!/usr/bin/python3

"""
WordNet load-process-save
Will have a normalizing effect, after which it's not modified

Author: John McCrae <john@mccr.ae> for original code
Author: Bernard Bou <1313ou@gmail.com> for rewrite and revamp
"""

#  Copyright (c) 2024-2026.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import argparse
import sys
import time
from collections.abc import Callable
from types import NoneType

from oewn_core.wordnet_fromyaml import load
from oewn_core.wordnet_toyaml import save

from oewn_core.wordnet import WordnetModel


def main(in_dir: str, out_dir: str, processf: Callable[[WordnetModel], WordnetModel]|NoneType = None) -> None:
    """
    WordNet load-process-save
    Will have a normalizing effect, after which it's not modified
    """
    wn = load(in_dir)
    if processf:
        print(f"Processing")
        processf(wn)
        print(f"Processed")
    save(wn, out_dir)


if __name__ == '__main__':
    start_time = time.time()
    arg_parser = argparse.ArgumentParser(description="load from yaml and save")
    arg_parser.add_argument('in_dir', type=str, help='from-dir')
    arg_parser.add_argument('out_dir', type=str, help='to-dir')
    args = arg_parser.parse_args()
    main(args.in_dir, args.out_dir)
    end_time = time.time()
    duration = end_time - start_time
    print(f"Conversion took {duration:.6f} seconds", file=sys.stderr)
