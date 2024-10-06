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

import wordnet_fromyaml as loader
import wordnet_toxml as saver


def yaml_to_xml1(in_dir, out_file):
    print(f'loading from YAML in {in_dir}')
    wn = loader.load(in_dir)
    print(f'loaded {wn} from YAML in {in_dir}')

    print(f'resolving cross-references')
    wn.resolve()
    print(f'resolved cross-references')
    print(f'extending relations')
    wn.extend()
    print(f'extended relations')

    print(wn)
    print(wn.info())

    print(f'saving to XML {out_file}')
    saver.save(wn, out_file)
    print(f'saved to XML {out_file}')


def main():
    arg_parser = argparse.ArgumentParser(description="load from yaml and save")
    arg_parser.add_argument('in_dir', type=str, help='from-dir')
    arg_parser.add_argument('out_file', type=str, help='to-file')
    args = arg_parser.parse_args()
    yaml_to_xml1(args.in_dir, args.out_file)


if __name__ == '__main__':
    main()
