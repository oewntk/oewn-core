#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import wordnet_xml as xml
from wordnet import Synset, Sense
from wordnet_xml import dash_factory, is_valid_xml_id


def collect_entries_for_escapes(entries, escape_map):
    r = {}
    for k in escape_map:
        if k == ' ':
            continue
        r[k] = []
        for e in entries:
            if k in e.lemma:
                r[k].append(e)
    return r


def print_as_dictionary(r, limit=5):
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


def make_dummy_sk(lemma):
    return make_sk(lemma, '1:00:00::')


def make_sk(lemma, lex_sense):
    return f'{lemma.lower().replace(' ', '_')}%{lex_sense}'


def is_valid_xsd_id(s):
    if not is_valid_xml_id(s):
        raise ValueError(f'Invalid xsd:id : {s} is not a valid XML ID')
    if ':' in s:
        raise ValueError(f"Invalid xsd:id : {s} contains colon ':'")
    return True


def is_parsable_sensekey(sk):
    try:
        l, s = xml.split_at_last(sk, '%')
        f = s.split(':')
        if len(f) == 5:
            return True
        raise ValueError(f'COLON: {sk.id}')
    except ValueError as ve:
        raise ValueError(f'PERCENT: {sk.id} {ve}')


def is_parsable_xml_sensekey(sk):
    try:
        l, s = xml.split_at_last(sk, dash_factory.xml_percent_sep)
        f = s.split(dash_factory.xml_colon_sep)
        if len(f) == 5:
            return True
        raise ValueError(f'COLON: {sk.id}')
    except ValueError as ve:
        raise ValueError(f'PERCENT: {sk.id} {ve}')
