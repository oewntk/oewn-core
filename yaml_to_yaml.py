#!/usr/bin/python3

"""
WordNet load-save
Will have a normalizing effect, after which it's idempotent

Author: John McCrae <john@mccr.ae> for original code
Author: Bernard Bou <1313ou@gmail.com> for rewrite and revamp
"""

#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import argparse
import wordnet_fromyaml as loader
import wordnet_toyaml as saver


def main():
    """
    WordNet load-save
    Will have a normalizing effect, after which it's idempotent
    """
    arg_parser = argparse.ArgumentParser(description="load from yaml and save")
    arg_parser.add_argument('in_dir', type=str, help='from-dir')
    arg_parser.add_argument('out_dir', type=str, help='to-dir')
    args = arg_parser.parse_args()

    print(f'loading from YAML in {args.in_dir}')
    wn = loader.load(args.in_dir)
    print(f'loaded {wn} from YAML in {args.in_dir}')

    print(f'resolving cross-references')
    wn.resolve()
    print(f'resolved cross-references')
    print(f'extending relations')
    wn.extend()
    print(f'extended relations')

    print(wn)
    print(wn.info())
    print(wn.info_relations())

    print(f'saving to YAML {args.out_dir}')
    saver.save(wn, args.out_dir)
    print(f'saved to YAML {args.out_dir}')


if __name__ == '__main__':
    main()
