#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite
import random
import unittest

import legacy
import model
import wordnet_xml


def make_xml_sensekeys(sk):
    esc_sk = wordnet_xml.escape_sensekey(sk)
    legacy_esc_sk = legacy.escape_sensekey(sk)
    return sk, esc_sk, legacy_esc_sk


def process(some_entries, factory, limit=3):
    for i, e in enumerate(some_entries):
        for s in e.senses:
            sk, esc_sk, legacy_esc_sk = factory(s.id)
            if i < limit:
                yield sk, esc_sk, legacy_esc_sk


class EscapeSchemesTestCase(unittest.TestCase):
    limit = 5

    def test_compare_escape_schemes(self):
        print('\nCOMPARE ESCAPE SCHEMES (RANDOM SELECTION)')
        some_entries = random.sample(model.entries, min(len(model.entries), 5))
        for sk, esc_sk, legacy_esc_sk in process(some_entries, make_xml_sensekeys, self.limit):
            print(f'\t{sk}')
            print(f'\t\t--now--> {esc_sk}')
            print(f'\t\t--leg--> {legacy_esc_sk}')

    def test_compare_escape_schemes_escapables(self):
        print('\nCOMPARE ESCAPE SCHEMES')
        r = model.collect_entries_for_escapes(model.entries, wordnet_xml.custom_char_escapes_for_sk)
        for k in r:
            v = r[k]
            if v:
                print(f'{k}')
                some_entries = random.sample(r[k], min(len(r[k]), 5))
                for sk, esc_sk, legacy_esc_sk in process(some_entries, make_xml_sensekeys, self.limit):
                    print(f'\t{sk}')
                    print(f'\t\t--now--> {esc_sk}')
                    print(f'\t\t--leg--> {legacy_esc_sk}')

    def test_escapables(self):
        print('\nTEST ESCAPE SCHEMES')
        r = model.collect_entries_for_escapes(model.entries, wordnet_xml.custom_char_escapes_for_sk)
        for k in r:
            v = r[k]
            if v:
                print(f'{k}')
                some_entries = random.sample(r[k], min(len(r[k]), 5))
                for sk, esc_sk, unesc_sk in process(some_entries, legacy.make_xml_sensekeys, self.limit):
                    print(f'\t{sk} --esc--> {esc_sk} --uesc--> {unesc_sk}')
