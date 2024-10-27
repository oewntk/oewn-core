#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

from oewn_xml import wordnet_xml as xml
from oewn_core.wordnet import Synset, Sense
from oewn_xml.wordnet_xml import dash_factory, is_valid_xml_id, to_xml_sense_id, from_xml_sense_id
from typing import Any, Dict, Tuple


def collect_entries_for_escapes(entries, escape_map) -> Dict[Any, list]:
    r = {}
    for k in escape_map:
        if k == ' ':
            continue
        r[k] = []
        for e in entries:
            if k in e.lemma:
                r[k].append(e)
    return r


def print_as_dictionary(r, limit=5) -> None:
    print('escapable = {')
    for k, v in r.items():
        print(f'\t"{k}": (')
        i = 0
        for e in v:
            if i > limit:
                print(f'\t\t# ... {len(r[k])} total')
                break
            print(f'\t\t{e.key},')
            i += 1
        print('\t),')
    print('}')


def dump(s: Synset | Sense):
    print(s)
    for r in sorted(s.relations, key=lambda r2: (r2.relation_type, r2.target)):
        print(f'\t{r}')


def make_dummy_sk(lemma) -> str:
    return make_sk(lemma, '1:00:00::')


def make_sk(lemma, lex_sense) -> str:
    return f'{lemma.lower().replace(' ', '_')}%{lex_sense}'


def is_valid_xsd_id(s) -> bool:
    if not is_valid_xml_id(s):
        raise ValueError(f'Invalid xsd:id : {s} is not a valid XML ID')
    if ':' in s:
        raise ValueError(f"Invalid xsd:id : {s} contains colon ':'")
    return True


def is_parsable_sensekey(sk) -> bool:
    try:
        l, s = xml.split_at_last(sk, '%')
        f = s.split(':')
        if len(f) == 5:
            return True
        raise ValueError(f'COLON: {sk.id}')
    except ValueError as ve:
        raise ValueError(f'PERCENT: {sk.id} {ve}')


def is_parsable_xml_sensekey(sk) -> bool:
    try:
        l, s = xml.split_at_last(sk, dash_factory.xml_percent_sep)
        f = s.split(dash_factory.xml_colon_sep)
        if len(f) == 5:
            return True
        raise ValueError(f'COLON: {sk.id}')
    except ValueError as ve:
        raise ValueError(f'PERCENT: {sk.id} {ve}')


def process_sensekey(sk: str) -> Tuple[str, str, str]:
    senseid = to_xml_sense_id(sk)
    sk2 = from_xml_sense_id(senseid)
    if sk != sk2:
        raise ValueError(f'unescaped != original: {sk} != {sk2}')
    return sk, senseid, sk2
