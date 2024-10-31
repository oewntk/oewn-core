#!/usr/bin/python3

"""
WordNet from-YAML utilities

Author: John McCrae <john@mccr.ae> for original code
Author: Bernard Bou <1313ou@gmail.com> for rewrite and revamp
"""
#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import argparse
import sys
import time
from glob import glob
from pathlib import Path
from typing import Any, Tuple, List, Dict

import yaml

from oewn_core.wordnet import WordnetModel, Entry, Sense, Synset, PartOfSpeech, Example, Pronunciation, VerbFrame


def load_verbframes(home: str) -> List[VerbFrame]:
    """
    Load verb frames from YAML
    :param home: home dir for YAML frame.yaml file
    :return: list of verb frames
    """
    with open(f'{home}/frames.yaml', encoding='utf-8') as inp:
        y: Dict[str, Any] = yaml.load(inp, Loader=yaml.CLoader)
        return [VerbFrame(k, v) for k, v in y.items()]


def load_entries(home: str) -> Tuple[List[Entry], Dict[str, Sense], Dict[Tuple[str, str], Entry]]:
    """
    Load entries from YAML
    :param home: home dir for YAML entries-*.yaml file
    :return: list of entries, sense resolver, member resolver
    """
    sense_resolver: Dict[str, Sense] = {}
    member_resolver: Dict[Tuple[str, str], Entry] = {}
    entries: List[Entry] = []
    for f in glob(f'{home}/entries-*.yaml'):
        with open(f, encoding='utf-8') as inp:
            y: Dict[str, Any] = yaml.load(inp, Loader=yaml.CLoader)
            for lemma, poses_discriminants in y.items():
                for pos_discriminant, entry_y in poses_discriminants.items():
                    pos = PartOfSpeech(pos_discriminant[:1]).value
                    discriminant = pos_discriminant[2:] if len(pos_discriminant) > 2 else None
                    entry = Entry(lemma, pos, discriminant)
                    if 'form' in entry_y:
                        entry.forms = entry_y['form']
                    if 'pronunciation' in entry_y:
                        entry.pronunciations = [Pronunciation(p['value'], p.get('variety')) for p in entry_y['pronunciation']]
                    for n, sense_y in enumerate(entry_y['sense']):
                        sense = load_sense(sense_y, entry)
                        entry.senses.append(sense)
                        sense_resolver[sense.id] = sense
                        member_resolver[(lemma, sense.synsetid)] = entry
                    entries.append(entry)
    return entries, sense_resolver, member_resolver


def load_synsets(home: str) -> Tuple[List[Synset], Dict[str, Synset]]:
    """
    Load synsets from YAML
    :param home: home dir for YAML (noun|verb|adj|adv))-*.yaml file
    :return: list of synsets, synset resolver
    """
    resolver: Dict[str, Synset] = {}
    synsets: List[Synset] = []
    noun_files = glob(f'{home}/noun*.yaml')
    verb_files = glob(f'{home}/verb*.yaml')
    adj_files = glob(f'{home}/adj*.yaml')
    adv_files = glob(f'{home}/adv*.yaml')
    for f in noun_files + verb_files + adj_files + adv_files:
        lex_name = Path(f).stem
        with open(f, encoding='utf-8') as inp:
            y: Dict[str, Any] = yaml.load(inp, Loader=yaml.CLoader)
            for synsetid, synset_y in y.items():
                synset = load_synset(synset_y, synsetid, lex_name)
                synsets.append(synset)
                resolver[synsetid] = synset
    return synsets, resolver


def load_sense(y: Dict[str, Any], entry: Entry) -> Sense:
    """
    Load sense from YAML
    :param y: properties provided by PyYAML
    :param entry: wrapping entry
    :return: sense
    """
    s = Sense(y['id'], entry, y['synset'], y.get('adjposition'))
    if 'sent' in y:
        s.examples = y['sent']
    if 'subcat' in y:
        s.verbframeids = y['subcat']
    # relations
    sense_rel_types: List[str] = [str(t) for t in Sense.Relation.Type]
    other_rel_types: List[str] = [str(t) for t in Sense.Relation.OtherType]
    for rel, targets in y.items():
        if rel in sense_rel_types:
            for target in targets:
                s.relations.append(Sense.Relation(target, Sense.Relation.Type(rel).value))
        if rel in other_rel_types:
            for target in targets:
                s.relations.append(Sense.Relation(target, Sense.Relation.OtherType(rel).value, True))
    return s


def load_synset(y: Dict[str, Any], synsetid: str, lex_name: str) -> Synset:
    """
    Load synset from YAML
    :param y: properties provided by PyYAML
    :param synsetid: synset ID
    :param lex_name: lexical name, provided by file name's stem
    :return: synset
    """
    pos = PartOfSpeech(y['partOfSpeech']).value
    ss = Synset(synsetid, pos, y['members'], lex_name)
    for defn in y['definition']:
        ss.definitions.append(defn)
    for example in y.get('example', []):
        if isinstance(example, str):
            ss.examples.append(example)
        else:
            ss.examples.append(Example(example['text'], example['source']))
    for usage in y.get('usage', []):
        ss.usages.append(usage)
    ss.source = y.get('source')
    ss.wikidata = y.get('wikidata')
    ss.ili = y.get('ili', 'in')
    # relations
    synset_rel_types: List[str] = [str(t) for t in Synset.Relation.Type]
    for rel, targets in y.items():
        if rel in synset_rel_types:
            for target in targets:
                ss.relations.append(Synset.Relation(target, Synset.Relation.Type(rel).value))
    return ss


def load_core(home: str) -> WordnetModel:
    """
    Load synset from YAML
    :param home: home dir for YAML *.yaml file
    :return: unresolved, unextended model
    """
    wn = WordnetModel('oewn', 'Open English Wordnet', 'en',
                      'english-wordnet@googlegroups.com',
                      'https://creativecommons.org/licenses/by/4.0',
                      '2024',
                      'https://github.com/globalwordnet/english-wordnet')
    # lex entries
    wn.entries, wn.sense_resolver, wn.member_resolver = load_entries(home)

    # synsets
    wn.synsets, wn.synset_resolver = load_synsets(home)

    # frames
    wn.verbframes = load_verbframes(home)

    return wn


def load(home: str, extend: bool=True, resolve: bool=False, verbose: bool = False) -> WordnetModel:
    if verbose:
        print(f'loading from YAML in {home}')
    wn = load_core(home)
    if verbose:
        print(f'loaded {wn} from YAML in {home}')
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


def main() -> WordnetModel:
    arg_parser = argparse.ArgumentParser(description="load from yaml")
    arg_parser.add_argument('in_dir', type=str, help='from-dir')
    args = arg_parser.parse_args()
    return load(args.in_dir)


if __name__ == '__main__':
    start_time = time.time()
    main()
    end_time = time.time()
    duration = end_time - start_time
    print(f"Loading took {duration:.6f} seconds", file=sys.stderr)
