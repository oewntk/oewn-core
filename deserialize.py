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

import wordnet_toyaml as saver


def load_pickle(path: str, file='wn.pickle'):
    """
    Load model from pickle file in path
    """
    with open(f"{path}/{file}", "rb") as out:
        return pickle.load(out)


def main():
    """
    WordNet load-save
    Will have a normalizing effect, after which it's not modified
    """
    arg_parser = argparse.ArgumentParser(description="load from yaml and save")
    arg_parser.add_argument('in_dir', type=str, help='from-dir for pickle')
    arg_parser.add_argument('pickle', type=str, nargs='?', default='oewn.pickle', help='from-pickle')
    args = arg_parser.parse_args()

    print(f'loading from pickle in {args.in_dir}')
    wn = load_pickle(args.in_dir)
    print(f'loading from pickle in {args.in_dir}')

    print(wn)
    print(wn.info())
    print(wn.info_relations())
    return wn


def test(wn, out_dir):
    print(f'saving to YAML {out_dir}')
    saver.save(wn, out_dir)
    print(f'saved to YAML {out_dir}')


if __name__ == '__main__':
    main()
