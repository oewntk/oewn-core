#!/usr/bin/python3

"""
Export SyntagNet collocation in OEWN YAML format
lex:
  pos-discriminant:
    sense:
      - collocation:
        - sensekey2a
        - sensekey2b
        ...
        id: sensekey1

abandon:
  v:
    sense:
    - collocation:
      - 'baby%1:18:00::'
      - 'car%1:06:00::'
      - 'favor%1:07:00::'
      - 'project%1:09:00::'
      - 'vehicle%1:06:00::'
      id: 'abandon%2:40:00::'

Author: Bernard Bou <1313ou@gmail.com> for rewrite and revamp
"""

#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import argparse
import codecs
import sys
import time
from typing import Dict, List, Any, Optional

import yaml

from oewn_core.wordnet import WordnetModel, Sense
from oewn_syntagnet.inject_syntagnet import load_and_inject


def sense_relations_to_yaml(sense: Sense) -> List[str]:
    """
    Build YAML dictionary for sense relation
    :param sense: sense
    :return: YAML dictionary or None if sense has no collocation
    """

    y: List[str] = []
    for r in sense.relations:
        if not r.other_type and Sense.Relation.Type(r.relation_type) == Sense.Relation.Type.COLLOCATION:
            y.append(r.target)
    return y


def sense_to_yaml(sense) -> Optional[Dict[str, Any]]:
    """
    Build YAML dictionary for sense
    :param sense: sense
    :return: YAML dictionary or None if sense has no collocation
    """

    yr: List[str] = sense_relations_to_yaml(sense)
    if yr:
        y: Dict[str, Any] = {'id': sense.id, 'collocation': yr}
        return y
    return None


def entry_to_yaml(entry) -> Optional[Dict[str, Any]]:
    """
    Build YAML dictionary for lexical entry
    :param entry: lexical entry
    :return: YAML dictionary
    """
    yss = [ys for s in entry.senses if (ys := sense_to_yaml(s)) is not None]
    if yss:
        return {'sense': yss}
    return None


def save_entries(wn: WordnetModel, home: str) -> None:
    """
    Persist entries to YAML (entries-(0|a|...|z).yaml
    :param wn: model
    :param home: home dir for persist files
    :return: None
    """
    y = {}
    for entry in wn.entries:
        # build
        ye = entry_to_yaml(entry)
        if ye:
            # first-tier key
            if entry.lemma not in y:
                y[entry.lemma] = {}
            # second-tier key
            key = f'{entry.pos}-{entry.discriminant}' if entry.discriminant else entry.pos
            if key not in y[entry.lemma]:
                y[entry.lemma][key] = {}

            y[entry.lemma][key] = ye

    # save
    with codecs.open(f'{home}/oewn-syntagnet.yaml', 'w', 'utf-8') as out:
        yaml.dump(y, out, allow_unicode=True)


def save(wn: WordnetModel, home: str) -> None:
    """
    Persist model to YAML syntagnet.yaml
    :param wn: model
    :param home: home dir for persist files
    """
    print(f'saving to YAML {home}')
    save_entries(wn, home)
    print(f'saved to YAML {home}')


def main() -> None:
    """
    Export SyntagNet as YAML
    """
    arg_parser = argparse.ArgumentParser(description="load wn and syntagnet from yaml, merge and save")
    arg_parser.add_argument('--pickle', action='store_true', default=False, help='use pickle')
    arg_parser.add_argument('in_dir', type=str, help='from-dir')
    arg_parser.add_argument('out_dir', type=str, help='to-dir')
    arg_parser.add_argument('syntagnet', type=str, help='collocations')
    arg_parser.add_argument('pickled', type=str, nargs='?', default=None, help='from-pickle')
    args = arg_parser.parse_args()

    wn: WordnetModel = load_and_inject(args.in_dir, args.syntagnet, args.pickled if args.pickle else None)
    save(wn, args.out_dir)


if __name__ == '__main__':
    start_time = time.time()
    main()
    end_time = time.time()
    duration = end_time - start_time
    print(f"Exporting took {duration:.6f} seconds", file=sys.stderr)
