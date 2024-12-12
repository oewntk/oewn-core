#!/usr/bin/python3

"""
WordNet load-save
Will have a normalizing effect, after which it's not modified

Author: John McCrae <john@mccr.ae> for original code
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
    Build dictionary for sense relation YAML
    :param sense: sense
    :return: dictionary or None if sense has no collocation
    """
    y: List[str] = []
    for r in sense.relations:
        if not r.other_type and Sense.Relation.Type(r.relation_type) == Sense.Relation.Type.COLLOCATION:
            y.append(r.target)
    return y


def sense_to_yaml(sense) -> Optional[Dict[str, Any]]:
    """
    Build dictionary for sense YAML
    :param sense: sense
    :return: dictionary or None if sense has no collocation
    """

    yr: List[str] = sense_relations_to_yaml(sense)
    if yr:
        y: Dict[str, Any] = {'id': sense.id, 'collocation': yr}
        return y
    return None


def entry_to_yaml(entry) -> Optional[Dict[str, Any]]:
    """
    Build dictionary for lexical entry YAML
    :param entry: lexical entry
    :return: dictionary
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
    with codecs.open(f'{home}/syntagnet.yaml', 'w', 'utf-8') as outp:
        outp.write(yaml.dump(y, allow_unicode=True))


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
    Save SyntagNet as YAML
    """
    arg_parser = argparse.ArgumentParser(description="load wn and syntagnet from yaml, merge and save")
    arg_parser.add_argument('in_dir', type=str, help='from-dir')
    arg_parser.add_argument('out_dir', type=str, help='to-dir')
    arg_parser.add_argument('syntagnet', type=str, help='collocations')
    args = arg_parser.parse_args()

    wn: WordnetModel = load_and_inject(args.in_dir, args.syntagnet)
    save(wn, args.out_dir)


if __name__ == '__main__':
    start_time = time.time()
    main()
    end_time = time.time()
    duration = end_time - start_time
    print(f"Importing took {duration:.6f} seconds", file=sys.stderr)
