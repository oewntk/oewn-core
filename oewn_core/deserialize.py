#!/usr/bin/python3
"""
WordNet deserialize

Author: John McCrae <john@mccr.ae> for original code
Author: Bernard Bou <1313ou@gmail.com> for rewrite and revamp
"""

#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import argparse
import pickle
import sys
import time

import oewn_core.wordnet_toyaml as saver


def load_pickle(path: str, file='wn.pickle'):
    """
    Load model from pickle file in path
    """
    with open(f"{path}/{file}", "rb") as out:
        return pickle.load(out)


def load(home: str, file='oewn.pickle', extend=True, resolve=False):
    print(f'loading from pickle {file} in {home}')
    wn = load_pickle(home, file=file)
    print(f'loaded {wn} from pickle {file} in {home}')
    if extend:
        print(f'extending relations')
        print(f'before extension: {wn.info_relations()}')
        wn.extend()
        print(f'after extension:  {wn.info_relations()}')
        print(f'extended relations')
    if resolve:
        print(f'resolving cross-references')
        wn.resolve()
        print(f'resolved cross-references')
    print(wn)
    print(wn.info())
    print(wn.info_relations())
    return wn


def main():
    """
    WordNet load-save
    Will have a normalizing effect, after which it's not modified
    """
    arg_parser = argparse.ArgumentParser(description="load from yaml and save")
    arg_parser.add_argument('in_dir', type=str, help='from-dir for pickle')
    arg_parser.add_argument('pickle', type=str, nargs='?', default='oewn.pickle', help='from-pickle')
    args = arg_parser.parse_args()
    return load(args.in_dir, args.pickle)


def test(wn, out_dir):
    print(f'saving to YAML {out_dir}')
    saver.save(wn, out_dir)
    print(f'saved to YAML {out_dir}')


if __name__ == '__main__':
    start_time = time.time()
    main()
    end_time = time.time()
    duration = end_time - start_time
    print(f"Loading took {duration:.6f} seconds", file=sys.stderr)
