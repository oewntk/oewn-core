#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite
import random
import unittest

from oewn_xml.wordnet_xml import dash_factory
from tests.model import wn
from tests.utils import collect_entries_for_escapes
from tests.legacy import make_xml_sensekeys as legacy_make_xml_sensekeys
from typing import Tuple, Generator


def process(some_entries, factory, limit=3) -> Generator[Tuple[str, str, str], None, None]:
    for i, e in enumerate(some_entries):
        for s in e.senses:
            sk, esc_sk, legacy_esc_sk = factory(s.id)
            if i < limit:
                yield sk, esc_sk, legacy_esc_sk


class EscapeSchemesTestCase(unittest.TestCase):
    limit = 5

    def test_compare_escape_schemes(self) -> None:
        print('\nCOMPARE ESCAPE SCHEMES (RANDOM SELECTION)')
        some_entries = random.sample(wn.entries, min(len(wn.entries), 5))
        for sk, esc_sk, legacy_esc_sk in process(some_entries, legacy_make_xml_sensekeys, self.limit):
            print(f'\t{sk}')
            print(f'\t\t--now--> {esc_sk}')
            print(f'\t\t--leg--> {legacy_esc_sk}')

    def test_compare_escape_schemes_escapables(self) -> None:
        print('\nCOMPARE ESCAPE SCHEMES')
        r = collect_entries_for_escapes(wn.entries, dash_factory.char_escapes_for_sk)
        for k in r:
            v = r[k]
            if v:
                print(f'{k}')
                some_entries = random.sample(r[k], min(len(r[k]), 5))
                for sk, esc_sk, legacy_esc_sk in process(some_entries, legacy_make_xml_sensekeys, self.limit):
                    print(f'\t{sk}')
                    print(f'\t\t--now--> {esc_sk}')
                    print(f'\t\t--leg--> {legacy_esc_sk}')

    def test_escapables(self) -> None:
        print('\nTEST ESCAPE SCHEMES')
        r = collect_entries_for_escapes(wn.entries, dash_factory.char_escapes_for_sk)
        for k in r:
            v = r[k]
            if v:
                print(f'{k}')
                some_entries = random.sample(r[k], min(len(r[k]), 5))
                for sk, esc_sk, unesc_sk in process(some_entries, legacy_make_xml_sensekeys, self.limit):
                    print(f'\t{sk} --esc--> {esc_sk} --unesc--> {unesc_sk}')
