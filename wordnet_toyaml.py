"""
WordNet to-YAML utilities

Author: John McCrae <john@mccr.ae> for original code
Author: Bernard Bou <1313ou@gmail.com> for rewrite and revamp
"""

#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import codecs
from typing import Set

import yaml

from wordnet import *

az = 'abcdefghijklmnopqrstuvwxyz'

ignored_symmetric_synset_relations: Set[Synset.Relation.Type] = {
    Synset.Relation.Type.HYPONYM,
    Synset.Relation.Type.INSTANCE_HYPONYM,
    Synset.Relation.Type.HOLONYM,
    Synset.Relation.Type.HOLO_LOCATION,
    Synset.Relation.Type.HOLO_MEMBER,
    Synset.Relation.Type.HOLO_PART,
    Synset.Relation.Type.HOLO_PORTION,
    Synset.Relation.Type.HOLO_SUBSTANCE,
    Synset.Relation.Type.STATE_OF,
    Synset.Relation.Type.IS_CAUSED_BY,
    Synset.Relation.Type.IS_SUBEVENT_OF,
    Synset.Relation.Type.IN_MANNER,
    Synset.Relation.Type.RESTRICTED_BY,
    Synset.Relation.Type.CLASSIFIED_BY,
    Synset.Relation.Type.IS_ENTAILED_BY,
    Synset.Relation.Type.HAS_DOMAIN_REGION,
    Synset.Relation.Type.HAS_DOMAIN_TOPIC,
    Synset.Relation.Type.IS_EXEMPLIFIED_BY,
    Synset.Relation.Type.INVOLVED,
    Synset.Relation.Type.INVOLVED_AGENT,
    Synset.Relation.Type.INVOLVED_PATIENT,
    Synset.Relation.Type.INVOLVED_RESULT,
    Synset.Relation.Type.INVOLVED_INSTRUMENT,
    Synset.Relation.Type.INVOLVED_LOCATION,
    Synset.Relation.Type.INVOLVED_DIRECTION,
    Synset.Relation.Type.INVOLVED_TARGET_DIRECTION,
    Synset.Relation.Type.INVOLVED_SOURCE_DIRECTION,
    Synset.Relation.Type.CO_PATIENT_AGENT,
    Synset.Relation.Type.CO_INSTRUMENT_AGENT,
    Synset.Relation.Type.CO_RESULT_AGENT,
    Synset.Relation.Type.CO_INSTRUMENT_PATIENT,
    Synset.Relation.Type.CO_INSTRUMENT_RESULT
}

ignored_symmetric_sense_relations: Set[Sense.Relation.Type] = {
    Sense.Relation.Type.HAS_DOMAIN_REGION,
    Sense.Relation.Type.HAS_DOMAIN_TOPIC,
    Sense.Relation.Type.IS_EXEMPLIFIED_BY
}

check_resolved = False
""" Whether resolved_* members' resolution is checked, a no-op because these are not saved """


def entry_to_yaml(entry, sense_resolver=None) -> Dict[str, str]:
    """
    Build dictionary for lexical entry YAML
    :param entry: lexical entry
    :param sense_resolver: if not None, sense resolution will we attempted
    :return: dictionary
    """
    e = {}
    if entry.forms:
        e['form'] = entry.forms
    if entry.pronunciations:
        e['pronunciation'] = []
        for p in entry.pronunciations:
            if p.variety:
                e['pronunciation'].append({'value': p.value, 'variety': p.variety})
            else:
                e['pronunciation'].append({'value': p.value})
    e['sense'] = [sense_to_yaml(s, sense_resolver) for s in entry.senses]
    return e


def sense_to_yaml(sense, sense_resolver=None) -> Dict[str, str]:
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
    if sense.sent:
        y['sent'] = sense.sent
    for r in sense.relations:
        if r.relation_type not in ignored_symmetric_sense_relations:
            t = r.relation_type
            if sense_resolver and (r.target not in sense_resolver):
                raise ValueError(f'Unresolved sense relation target {r.target} of type {t} in {sense.id}')
            if check_resolved and sense_resolver and (
                    r.target not in sense_resolver or sense_resolver[r.target] != r.resolved_target):
                raise ValueError(f'Invalid sense relation resolved target {r.target} of type {t} in {sense.id}')
            if t not in y:
                y[t] = []
            y[t].append(r.target)
    return y


def synset_to_yaml(synset, synset_resolver=None, member_resolver=None) -> Dict[str, str]:
    """
    Build dictionary for synset YAML
    :param synset: synset
    :param synset_resolver: if not None, synset resolution will be attempted and checked
    :param member_resolver: if not None, member resolution will be attempted and checked
    :return: dictionary
    """
    if member_resolver and not all((m, synset.id) in member_resolver for m in synset.members):
        raise ValueError(f'Unresolved member in {synset.members}')

    y = {'members': synset.members,
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
    for r in synset.relations:
        if r.relation_type not in ignored_symmetric_synset_relations:
            t = r.relation_type
            if synset_resolver and r.target not in synset_resolver:
                raise ValueError(f'Unresolved synset relation target {r.target} of type {t} in {synset.id}')
            if check_resolved and synset_resolver and (
                    r.target not in synset_resolver or synset_resolver[r.target] != r.resolved_target):
                raise ValueError(f'Invalid synset relation resolved target {r.target} of type {t} in {synset.id}')
            if t not in y:
                y[t] = []
            y[t].append(r.target)
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
        pos_discriminant = f'{entry.pos}{entry.discriminant if entry.discriminant else ''}'
        if pos_discriminant in entry_yaml[first][entry.lemma]:
            raise ValueError(f'Duplicate entry: {entry.lemma}-{pos_discriminant}')

        entry_yaml[first][entry.lemma][pos_discriminant] = y

    # save
    for c in az:
        with codecs.open(f'{home}/entries-%s.yaml' % c, 'w', 'utf-8') as outp:
            outp.write(yaml.dump(entry_yaml[c], allow_unicode=True))
    with codecs.open(f'{home}/entries-0.yaml', 'w', 'utf-8') as outp:
        outp.write(yaml.dump(entry_yaml['0'], allow_unicode=True))


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
            out.write(yaml.dump(synsets, allow_unicode=True))


def save_verbframes(wn: WordnetModel, home: str) -> None:
    """
    Persist verb frames to YAML frame.yaml
    :param wn: model
    :param home: home dir for persist file
     """
    frame_yaml = {b.id: b.verbframe for b in wn.verbframes}
    with open(f'{home}/frames.yaml', 'w', encoding='utf-8') as out:
        out.write(yaml.dump(frame_yaml, allow_unicode=True))


def save(wn: WordnetModel, home: str) -> None:
    """
    Persist model to YAML *.yaml
    :param wn: model
    :param home: home dir for persist files
    """
    save_entries(wn, home)
    save_synsets(wn, home)
    save_verbframes(wn, home)
