"""
WordNet compare escape schemes
Author: John McCrae <john@mccr.ae> for original code
Author: Bernard Bou <1313ou@gmail.com> for rewrite and revamp
"""
#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import random
import unittest
from typing import Tuple, Generator

from oewn_xml.wordnet_xml import dash_factory, is_valid_xml_id
from tests.model import wn
from tests.utils import collect_entries_for_escapes, is_valid_xsd_id, generate_legacy_senseid_from_sensekey, generate_senseid_from_sensekey


def generate_senseids(some_entries, limit=3) -> Generator[Tuple[str, str, str], None, None]:
    """ Produces senseids for comparison"""
    for i, e in enumerate(some_entries):
        for s in e.senses:
            sk, senseid, unesc_sk = generate_senseid_from_sensekey(s.id)
            sk, legacy_senseid, legacy_unesc_sk = generate_legacy_senseid_from_sensekey(s.id)
            if i < limit:
                yield sk, senseid, legacy_senseid


class EscapeSchemesTestCase(unittest.TestCase):
    limit = 5

    def test_compare_escape_schemes_on_random_samples(self) -> None:
        print('\nCOMPARE ESCAPE SCHEMES (RANDOM SELECTION)')
        some_entries = random.sample(wn.entries, min(len(wn.entries), 5))
        for sk, senseid, legacy_senseid in generate_senseids(some_entries, self.limit):
            print(f'\t{sk}')
            print(f'\t\t--now--> {senseid}')
            print(f'\t\t--leg--> {legacy_senseid}')

    def test_compare_escape_schemes_escapables_on_escape_cases(self) -> None:
        print('\nCOMPARE ESCAPE SCHEMES')
        r = collect_entries_for_escapes(wn.entries, dash_factory.char_escapes_for_sk)
        for k in r:
            v = r[k]
            if v:
                print(f'{k}')
                some_entries = random.sample(r[k], min(len(r[k]), 5))
                for sk, senseid, legacy_senseid in generate_senseids(some_entries, self.limit):
                    print(f'\t{sk}')
                    print(f'\t\t--now--> {senseid}')
                    print(f'\t\t--leg--> {legacy_senseid}')

    def test_validity_on_escapables(self) -> None:
        print('\nTEST ESCAPE SCHEMES')
        r = collect_entries_for_escapes(wn.entries, dash_factory.char_escapes_for_sk)
        for k in r:
            v = r[k]
            if v:
                print(f'{k}')
                some_entries = random.sample(r[k], min(len(r[k]), 5))
                for sk, senseid, legacy_senseid in generate_senseids(some_entries, self.limit):
                    print(f'\t{sk} --senseid--> {senseid}')
                    self.assertTrue(is_valid_xml_id(senseid), f'{sk} --senseid--> {senseid}')
                    self.assertTrue(is_valid_xsd_id(senseid), f'{sk} --senseid--> {senseid}')
                    print(f'\t{sk} --legacy senseid--> {legacy_senseid}')
                    self.assertTrue(is_valid_xml_id(legacy_senseid), f'{sk}--legacy senseid--> {legacy_senseid}')
                    self.assertTrue(is_valid_xsd_id(legacy_senseid), f'{sk}--legacy senseid--> {legacy_senseid}')
