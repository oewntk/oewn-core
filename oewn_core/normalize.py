#!/usr/bin/python3

"""
WordNet persistence

Author: John McCrae <john@mccr.ae> for original code
Author: Bernard Bou <1313ou@gmail.com> for rewrite and revamp
"""

#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import argparse
import glob
import sys
import time

import yaml


def normalize(home: str, verbose: bool = False) -> None:
    """ Normalize (home dir)"""
    if verbose:
        print(f'normalizing YAML in {home}')
    for f in glob.glob(f"{home}/*.yaml"):
        data = yaml.load(open(f), Loader=yaml.CLoader)
        with open(f, "w", encoding='utf-8') as out:
            yaml.dump(data, out, allow_unicode=True)
    if verbose:
        print(f'normalized YAML in {home}')


def main() -> None:
    """
    WordNet normalize
    Will test YAML well-formedness
    Will have a limited normalizing effect, after which it's not modified
    YAML keys are not alphabetically reordered,
    turn to load()-save() if this is desired
    """
    arg_parser = argparse.ArgumentParser(description="load from yaml and save")
    arg_parser.add_argument('in_dir', type=str, help='from-dir')
    args = arg_parser.parse_args()
    normalize(args.in_dir)

if __name__ == '__main__':
    start_time = time.time()
    main()
    end_time = time.time()
    duration = end_time - start_time
    print(f"Normalizing took {duration:.6f} seconds", file=sys.stderr)
