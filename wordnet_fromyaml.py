"""
WordNet from-YAML utilities

Author: John McCrae <john@mccr.ae> for original code
Author: Bernard Bou <1313ou@gmail.com> for rewrite and revamp
"""

#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

from glob import glob
from pathlib import Path
from typing import Any

import yaml

from wordnet import *


def load_verbframes(home: str):
    with open(f'{home}/frames.yaml', encoding='utf-8') as inp:
        frames = yaml.load(inp, Loader=yaml.CLoader)
        return [VerbFrame(k, v) for k, v in frames.items()]


def load_entries(home: str) -> Tuple[List[Entry], Dict[str, Sense], Dict[Tuple[str, str], Entry]]:
    sense_resolver: Dict[str, Sense] = {}
    member_resolver: Dict[Tuple[str, str], Entry] = {}
    entries: List[Entry] = []
    for f in glob(f'{home}/entries-*.yaml'):
        with open(f, encoding='utf-8') as inp:
            y = yaml.load(inp, Loader=yaml.CLoader)
            for lemma, poses_discriminants in y.items():
                for pos_discriminant, props in poses_discriminants.items():
                    pos = PartOfSpeech(pos_discriminant[:1]).value
                    discriminant = pos_discriminant[1:]
                    entry = Entry(lemma, pos, discriminant)
                    if 'form' in props:
                        entry.forms = props['form']
                    if 'pronunciation' in props:
                        entry.pronunciations = [Pronunciation(p['value'], p.get('variety')) for p in
                                                props['pronunciation']]
                    for n, sense_props in enumerate(props['sense']):
                        sense = load_sense(sense_props, entry, n)
                        entry.senses.append(sense)
                        sense_resolver[sense.id] = sense
                        member_resolver[(lemma, sense.synsetid)] = entry
                    entries.append(entry)
    return entries, sense_resolver, member_resolver


def load_synsets(home: str) -> Tuple[List[Synset], Dict[str, Synset]]:
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
            for synsetid, props in y.items():
                synset = load_synset(props, synsetid, lex_name)
                synsets.append(synset)
                resolver[synsetid] = synset
    return synsets, resolver


def load_sense(props: Dict[str, Any], entry: Entry, n: int):
    s = Sense(props['id'], entry, props['synset'], n, props.get('adjposition'))
    if 'sent' in props:
        s.sent = props['sent']
    if 'subcat' in props:
        s.subcat = props['subcat']
    # relations
    sense_rel_types = [t.value for t in Sense.Relation.Type]
    other_rel_types = [t.value for t in Sense.Relation.OtherType]
    for rel, targets in props.items():
        if rel in sense_rel_types:
            for target in targets:
                s.relations.append(Sense.Relation(target, Sense.Relation.Type(rel).value))
        if rel in other_rel_types:
            for target in targets:
                s.relations.append(Sense.Relation(target, Sense.Relation.OtherType(rel).value, True))
    return s


def load_synset(props: Dict[str, Any], synsetid: str, lex_name: str):
    pos = PartOfSpeech(props['partOfSpeech']).value
    ss = Synset(synsetid, pos, props['members'], lex_name)
    for defn in props['definition']:
        ss.definitions.append(defn)
    for example in props.get('example', []):
        if isinstance(example, str):
            ss.examples.append(example)
        else:
            ss.examples.append(Example(example['text'], example['source']))
    for usage in props.get('usage', []):
        ss.usages.append(usage)
    ss.source = props.get('source')
    ss.wikidata = props.get('wikidata')
    ss.ili = props.get('ili', 'in')
    # relations
    synset_rel_types = [t.value for t in Synset.Relation.Type]
    for rel, targets in props.items():
        if rel in synset_rel_types:
            for target in targets:
                ss.relations.append(Synset.Relation(target, Synset.Relation.Type(rel).value))
    return ss


def load(home: str):
    wn = WordnetModel('oewn', 'Open English Wordnet', 'en',
                      'english-wordnet@googlegroups.com',
                      'https://creativecommons.org/licenses/by/4.0',
                      '2024',
                      'https://github.com/globalwordnet/english-wordnet')
    # frames
    wn.frames = load_verbframes(home)

    # lex entries
    wn.entries, wn.sense_resolver, wn.member_resolver = load_entries(home)

    # synsets
    wn.synsets, wn.synset_resolver = load_synsets(home)
    return wn


def main():
    wn = load('src/yaml')
    wn.resolve()
    print(wn)
    print(wn.info)


if __name__ == '__main__':
    main()
