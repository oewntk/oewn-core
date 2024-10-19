#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import os
import sys
import unittest

import deserialize
import wordnet_xml

data_home = os.environ['OEWN_HOME']
print(f'data={data_home}', file=sys.stderr)
wn = deserialize.load_pickle(data_home)
entries = sorted(list(wn.entries), key=lambda e: e.lemma)


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


def check_sense(s):
    sk = s.id
    esc_sk = wordnet_xml.escape_sensekey(sk)
    unesc_sk = wordnet_xml.unescape_sensekey(esc_sk)
    if sk != unesc_sk:
        raise ValueError(f'unescaped != original: {sk} != {unesc_sk}')
    return sk, esc_sk, unesc_sk


class EscapablesTestCase(unittest.TestCase):
    limit = 5

    def test_escapables(self):
        r = collect_entries_for_escapes(entries, wordnet_xml.custom_char_escapes_for_sk)
        print_as_dictionary(r)
        for k in r:
            v = r[k]
            if v:
                print(f'{k}')
                for i, e in enumerate(r[k]):
                    for s in e.senses:
                        sk, esc_sk, unesc_sk = check_sense(s)
                        if i < self.limit:
                            print(f'\t{sk} --xml-->  {esc_sk} --reverse-->  {unesc_sk}')
