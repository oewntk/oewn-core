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

import wordnet_fromxml as loader
import wordnet_toyaml as saver


def xml1_to_yaml(in_file, out_dir):
    print(f'loading from XML {in_file}')
    wn = loader.load(in_file)
    print(f'loaded {wn} from XML {in_file}')

    print(wn)
    print(wn.info())
    print(wn.info_relations())

    print(f'saving to YAML in {out_dir}')
    saver.save(wn, out_dir)
    print(f'saved to YAML in {out_dir}')


def main():
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
