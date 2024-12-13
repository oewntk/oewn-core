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

from oewn_core.wordnet import WordnetModel


def load_pickle(path: str, file='wn.pickle') -> WordnetModel:
    """
    Load model from pickle file in path
    """
    with open(f"{path}/{file}", "rb") as out:
        return pickle.load(out)


def load(home: str, file='oewn.pickle', extend: bool = True, resolve: bool = False, verbose: bool = False) -> WordnetModel:
    if verbose:
        print(f'loading from pickle {file} in {home}')
    wn = load_pickle(home, file=file)
    if verbose:
        print(f'loaded {wn} from pickle {file} in {home}')
    if extend:
        if verbose:
            print(f'extending relations')
            print(f'before extension: {wn.info_relations()}')
        wn.extend()
        if verbose:
            print(f'after extension:  {wn.info_relations()}')
            print(f'extended relations')
    if resolve:
        if verbose:
            print(f'resolving cross-references')
        wn.resolve()
        if verbose:
            print(f'resolved cross-references')
    if verbose:
        print(wn)
        print(wn.info())
        print(wn.info_relations())
    return wn


def test(wn, out_dir) -> None:
    import oewn_core.wordnet_toyaml as saver
    saver.save(wn, out_dir)


def main() -> WordnetModel:
    """
    WordNet load-save
    Will have a normalizing effect, after which it's not modified
    """
    arg_parser = argparse.ArgumentParser(description="load from yaml and save")
    arg_parser.add_argument('in_dir', type=str, help='from-dir for pickle')
    arg_parser.add_argument('pickled', type=str, nargs='?', default='oewn.pickle', help='from-pickle')
    args = arg_parser.parse_args()
    return load(args.in_dir, args.pickled)


if __name__ == '__main__':
    start_time = time.time()
    main()
    end_time = time.time()
    duration = end_time - start_time
    print(f"Loading took {duration:.6f} seconds", file=sys.stderr)
