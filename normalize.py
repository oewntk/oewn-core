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

import yaml


def normalize(home: str):
    """ Normalize (home dir)"""
    for f in glob.glob(f"{home}/*.yaml"):
        data = yaml.load(open(f), Loader=yaml.CLoader)
        with open(f, "w", encoding='utf-8') as out:
            out.write(yaml.dump(data, allow_unicode=True))


def main():
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

    print(f'normalizing YAML in {args.in_dir}')
    normalize(args.in_dir)
    print(f'normalized YAML in {args.in_dir}')


if __name__ == '__main__':
    main()
