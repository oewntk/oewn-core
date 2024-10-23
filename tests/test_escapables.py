#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import unittest

import model
import wordnet_xml
from wordnet_xml import DashNameFactory


def process_sensekey(sk):
    esc_sk = wordnet_xml.escape_sensekey(sk)
    unesc_sk = wordnet_xml.unescape_sensekey(esc_sk)
    if sk != unesc_sk:
        raise ValueError(f'unescaped != original: {sk} != {unesc_sk}')
    return sk, esc_sk, unesc_sk


class EscapablesTestCase(unittest.TestCase):
    limit = 5

    def test_escapables(self):
        r = model.collect_entries_for_escapes(model.wn.entries, DashNameFactory.char_escapes_for_sk)
        model.print_as_dictionary(r)
        for k in r:
            v = r[k]
            if v:
                print(f'{k}')
                for i, e in enumerate(r[k]):
                    for s in e.senses:
                        sk, esc_sk, unesc_sk = process_sensekey(s.id)
                        if i < self.limit:
                            print(f'\t{sk} --xml-->  {esc_sk} --reverse-->  {unesc_sk}')
