"""
WordNet to-YAML utilities

Author: John McCrae <john@mccr.ae> for original code
Author: Bernard Bou <1313ou@gmail.com> for rewrite and revamp
"""

#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import codecs
from typing import Dict, List, Any

import yaml

from oewn_core.wordnet import WordnetModel, Sense, Synset, Example, ignored_symmetric_sense_relations, ignored_symmetric_synset_relations

az = 'abcdefghijklmnopqrstuvwxyz'

check_resolved = False
""" Whether resolved_* members' resolution is checked, a no-op because these are not saved """


def entry_to_yaml(entry, sense_resolver=None) -> Dict[str, Any]:
    """
    Build dictionary for lexical entry YAML
    :param entry: lexical entry
    :param sense_resolver: if not None, sense resolution will we attempted
    :return: dictionary
    """
    y = {}
    if entry.forms:
        y['form'] = entry.forms
    if entry.pronunciations:
        y['pronunciation'] = []
        for p in entry.pronunciations:
            if p.variety:
                y['pronunciation'].append({'value': p.value, 'variety': p.variety})
            else:
                y['pronunciation'].append({'value': p.value})
    y['sense'] = [sense_to_yaml(s, sense_resolver) for s in entry.senses]
    return y


def sense_to_yaml(sense, sense_resolver=None) -> Dict[str, Any]:
    """
    Build dictionary for sense YAML
    :param sense: sense
    :param sense_resolver: if not None, sense resolution will be attempted and checked
    :return: dictionary
    """
    y = {'id': sense.id, 'synset': sense.synsetid, }
    if sense.adjposition:
        y['adjposition'] = sense.adjposition
    if sense.verbframeids:
        y['subcat'] = sense.verbframeids
    if sense.examples:
        y['sent'] = sense.examples
    yr: Dict[str, List[str]] = sense_relations_to_yaml(sense, sense_resolver)
    if yr:
        y.update(yr)
    return y


def synset_to_yaml(synset, synset_resolver=None, member_resolver=None) -> Dict[str, Any]:
    """
    Build dictionary for synset YAML
    :param synset: synset
    :param synset_resolver: if not None, synset resolution will be attempted and checked
    :param member_resolver: if not None, member resolution will be attempted and checked
    :return: dictionary
    """
    if member_resolver and not all((m, synset.id) in member_resolver for m in synset.members):
        raise ValueError(f'Unresolved member in {synset.members}')

    y = {
        'members': synset.members,
        'partOfSpeech': synset.pos,
        'definition': synset.definitions
    }
    if synset.examples:
        y['example'] = [example_to_yaml(x) for x in synset.examples]
    if synset.usages:
        y['usage'] = synset.usages
    if synset.wikidata:
        y['wikidata'] = synset.wikidata
    if synset.source:
        y['source'] = synset.source
    if synset.ili and synset.ili != 'in':
        y['ili'] = synset.ili
    yr: Dict[str, List[str]] = synset_relations_to_yaml(synset, synset_resolver)
    if yr:
        y.update(yr)
    return y


def sense_relations_to_yaml(sense: Sense, sense_resolver=None) -> Dict[str, List[str]]:
    y: Dict[str, List[str]] = {}
    for r in sense.relations:
        t = Sense.Relation.OtherType(r.relation_type) if r.other_type else Sense.Relation.Type(r.relation_type)
        if t not in ignored_symmetric_sense_relations:
            if sense_resolver and (r.target not in sense_resolver):
                raise ValueError(f'Unresolved sense relation target {r.target} of type {t.value} in {sense.id}')
            if check_resolved and sense_resolver and (
                    r.target not in sense_resolver or sense_resolver[r.target] != r.resolved_target):
                raise ValueError(f'Invalid sense relation resolved target {r.target} of type {t.value} in {sense.id}')
            k: str = str(t.value)
            if k not in y:
                y[k] = []
            y[k].append(r.target)
    return y


def synset_relations_to_yaml(synset: Synset, synset_resolver=None) -> Dict[str, List[str]]:
    y: Dict[str, List[str]] = {}
    for r in synset.relations:
        t = Synset.Relation.Type(r.relation_type)
        if t not in ignored_symmetric_synset_relations:
            if synset_resolver and r.target not in synset_resolver:
                raise ValueError(f'Unresolved synset relation target {r.target} of type {t.value} in {synset.id}')
            if check_resolved and synset_resolver and (
                    r.target not in synset_resolver or synset_resolver[r.target] != r.resolved_target):
                raise ValueError(f'Invalid synset relation resolved target {r.target} of type {t.value} in {synset.id}')
            k: str = str(t.value)
            if t.value not in y:
                y[k] = []
            y[k].append(r.target)
    return y


def example_to_yaml(example: str | Example) -> Dict[str, str] | str:
    """
    Build dictionary for sourced example or text for unsourced example YAML
    :param example: example
    :return: dictionary or string
    """
    if isinstance(example, Example):
        return {'text': example.text, 'source': example.source} if example.source else example.text
    return example


def save_entries(wn: WordnetModel, home: str) -> None:
    """
    Persist entries to YAML (entries-(0|a|...|z).yaml
    :param wn: model
    :param home: home dir for persist files
    :return: None
    """
    sense_resolver = wn.sense_resolver if wn.sense_resolver else None
    entry_yaml = {c: {} for c in az}
    entry_yaml['0'] = {}
    for entry in wn.entries:
        # build
        y = entry_to_yaml(entry, sense_resolver=sense_resolver)

        # locate
        first = entry.lemma.lower()[:1]
        if first not in az:
            first = '0'

        # super dict
        if entry.lemma not in entry_yaml[first]:
            entry_yaml[first][entry.lemma] = {}

        # uniqueness
        key = f'{entry.pos}-{entry.discriminant}' if entry.discriminant else entry.pos
        if key in entry_yaml[first][entry.lemma]:
            raise ValueError(f'Duplicate entry: {entry.lemma}-{key}')

        entry_yaml[first][entry.lemma][key] = y

    # save
    for c in az:
        with codecs.open(f'{home}/entries-%s.yaml' % c, 'w', 'utf-8') as out:
            yaml.dump(entry_yaml[c], out, allow_unicode=True)
    with codecs.open(f'{home}/entries-0.yaml', 'w', 'utf-8') as out:
        yaml.dump(entry_yaml['0'], out, allow_unicode=True)


def save_synsets(wn: WordnetModel, home: str) -> None:
    """
    Persist synsets to YAML (noun|verb|adj|adv)*.yaml
    :param wn: model
    :param home: home dir for persist files
    """
    synset_yaml = {}
    for synset in wn.synsets:
        # build
        y = synset_to_yaml(synset, synset_resolver=wn.synset_resolver, member_resolver=wn.member_resolver)

        # super dict
        if synset.lex_name not in synset_yaml:
            synset_yaml[synset.lex_name] = {}

        # uniqueness
        if synset.id in synset_yaml[synset.lex_name]:
            raise ValueError(f'Duplicate synset: {synset.id} in {synset.lex_name}')
        synset_yaml[synset.lex_name][synset.id] = y

    # save
    for key, synsets in synset_yaml.items():
        with codecs.open(f'{home}/%s.yaml' % key, 'w', 'utf-8') as out:
            yaml.dump(synsets, out, allow_unicode=True)


def save_verbframes(wn: WordnetModel, home: str) -> None:
    """
    Persist verb frames to YAML frame.yaml
    :param wn: model
    :param home: home dir for persist file
     """
    frame_yaml = {b.id: b.verbframe for b in wn.verbframes}
    with open(f'{home}/frames.yaml', 'w', encoding='utf-8') as out:
        yaml.dump(frame_yaml, out, allow_unicode=True)


def save(wn: WordnetModel, home: str) -> None:
    """
    Persist model to YAML *.yaml
    :param wn: model
    :param home: home dir for persist files
    """
    print(f'saving to YAML {home}')
    save_entries(wn, home)
    save_synsets(wn, home)
    save_verbframes(wn, home)
    print(f'saved to YAML {home}')
