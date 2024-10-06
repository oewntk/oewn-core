#!/usr/bin/python3
"""
WordNet persistence

Author: John McCrae <john@mccr.ae> for original code
Author: Bernard Bou <1313ou@gmail.com> for rewrite and revamp
"""

#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import glob
from _typeshed import SupportsWrite

import yaml
import pickle

from wordnet import WordnetModel


def normalize(home: str):
    """ Normalize (home dir)"""
    for f in glob.glob(f"{home}/*.yaml"):
        data = yaml.load(open(f), Loader=yaml.CLoader)
        with open(f, "w", encoding='utf-8') as out:
            out.write(yaml.dump(data, allow_unicode=True))


def load_pickle(path: str, file='wn.pickle'):
    """ Load model from pickle file in path """
    with open(f"{path}/{file}", "rb") as out:
        return pickle.load(out)


def save_pickle(wn: WordnetModel, path: str, file: str='wn.pickle'):
    """ Save model to pickle file in path """
    with open(f'{path}/{file}', 'wb') as out: # type: SupportsWrite[bytes]
        pickle.dump(wn, out)
