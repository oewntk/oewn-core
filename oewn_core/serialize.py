#!/usr/bin/python3

"""
WordNet serialize

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
from oewn_core.wordnet_fromyaml import load


def save_pickle(wn: WordnetModel, path: str, file: str = 'wn.pickle', verbose: bool = False) -> None:
    """
    Save model to pickle file in path
    Cross-references don't have to be staled.
    """
    if verbose:
        print(f'saving to pickle in {path}/{file}')
    with open(f'{path}/{file}', 'wb') as out:
        pickle.dump(wn, out)
    if verbose:
        print(f'saved to pickle in {path}/{file}')


def main() -> WordnetModel:
    """
    WordNet load-save
    Will have a normalizing effect, after which it's not modified
    """
    arg_parser = argparse.ArgumentParser(description="load from yaml and save")
    arg_parser.add_argument('in_dir', type=str, help='from-dir')
    arg_parser.add_argument('out_dir', type=str, help='to-dir for pickle')
    arg_parser.add_argument('pickled', type=str, nargs='?', default='oewn.pickle', help='to-pickle')
    args = arg_parser.parse_args()

    wn = load(args.in_dir)
    save_pickle(wn, args.out_dir, args.pickled)
    return wn


def test(out_dir, verbose: bool = False) -> None:
    from oewn_core.deserialize import load_pickle
    if verbose:
        print(f'loading from pickle in {out_dir}')
    wn = load_pickle(out_dir)
    if verbose:
        print(f'loading from pickle in {out_dir}')
        print(wn)
        print(wn.info())
        print(wn.info_relations())


if __name__ == '__main__':
    start_time = time.time()
    main()
    end_time = time.time()
    duration = end_time - start_time
    print(f"Saving took {duration:.6f} seconds", file=sys.stderr)
