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
import copyreg
import pickle

import wordnet_fromyaml as loader
from wordnet import WordnetModel, Sense, Synset


def pickle_sense(sense: Sense):
    """
    # Return a tuple containing the class and a reduced state without 'resolved_synset'
    """
    state = sense.__dict__.copy()
    state.pop('resolved_synset', None)  # attribute not to pickle
    return Sense, (state,)


def pickle_synset(sense: Synset):
    """
    # Return a tuple containing the class and a reduced state without 'resolved_members'
    """
    state = sense.__dict__.copy()
    state.pop('resolved_members', None)  # attribute not to pickle
    return Synset, (state,)


def pickle_relation(relation: Synset.Relation | Sense.Relation):
    """
    # Return a tuple containing the class and a reduced state without 'resolved_target'
    """
    state = relation.__dict__.copy()
    state.pop('resolved_target', None)  # attribute not to pickle
    return type(relation), (state,)


def load_pickle(path: str, file='wn.pickle'):
    """ Load model from pickle file in path """
    with open(f"{path}/{file}", "rb") as out:
        return pickle.load(out)


def save_pickle(wn: WordnetModel, path: str, file: str = 'wn.pickle'):
    """
    Save model to pickle file in path
    Cross-references don't have to be staled.
    """
    copyreg.pickle(Sense, pickle_sense)
    copyreg.pickle(Synset, pickle_synset)
    copyreg.pickle(Synset.Relation, pickle_relation)
    copyreg.pickle(Sense.Relation, pickle_relation)

    with open(f'{path}/{file}', 'wb') as out:  # type: SupportsWrite[bytes]
        pickle.dump(wn, out)


def main():
    """
    WordNet load-save
    Will have a normalizing effect, after which it's not modified
    """
    arg_parser = argparse.ArgumentParser(description="load from yaml and save")
    arg_parser.add_argument('in_dir', type=str, help='from-dir')
    arg_parser.add_argument('out_dir', type=str, help='out_dir')
    arg_parser.add_argument('pickle', type=str, nargs='?', default='oewn.pickle', help='to-pickle')
    args = arg_parser.parse_args()

    print(f'loading from YAML in {args.in_dir}')
    wn = loader.load(args.in_dir)
    print(f'loaded {wn} from YAML in {args.in_dir}')

    print(f'resolving cross-references')
    wn.resolve()
    print(f'resolved cross-references')

    print(wn)
    print(wn.info())
    print(wn.info_relations())

    print(f'saving to pickle {args.out_dir}')
    save_pickle(wn, args.out_dir)
    print(f'saved to pickle {args.out_dir}')

    print(f'loading from pickle in {args.out_dir}')
    wn2 = load_pickle(args.out_dir)
    print(f'loading from pickle in {args.out_dir}')

    print(wn2)
    print(wn2.info())
    print(wn2.info_relations())


if __name__ == '__main__':
    main()
