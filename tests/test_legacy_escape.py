#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite
import random
import unittest
from typing import Tuple, Generator

from oewn_xml.wordnet_xml import dash_factory
from tests.legacy import process_sensekey as legacy_process_sensekey
from tests.model import wn
from tests.utils import collect_entries_for_escapes
from tests.utils import process_sensekey as process_sensekey


def process(some_entries, limit=3) -> Generator[Tuple[str, str, str], None, None]:
    for i, e in enumerate(some_entries):
        for s in e.senses:
            sk, legacy_senseid, legacy_unesc_sk = legacy_process_sensekey(s.id)
            sk, senseid, unesc_sk = process_sensekey(s.id)
            if i < limit:
                yield sk, senseid, legacy_senseid


class EscapeSchemesTestCase(unittest.TestCase):
    limit = 5

    def test_compare_escape_schemes(self) -> None:
        print('\nCOMPARE ESCAPE SCHEMES (RANDOM SELECTION)')
        some_entries = random.sample(wn.entries, min(len(wn.entries), 5))
        for sk, esc_sk, legacy_esc_sk in process(some_entries, self.limit):
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
                for sk, esc_sk, legacy_esc_sk in process(some_entries, self.limit):
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
                for sk, esc_sk, unesc_sk in process(some_entries, self.limit):
                    print(f'\t{sk} --esc--> {esc_sk} --unesc--> {unesc_sk}')
