"""
WordNet tests for escapable sequences found in OEWN
Author: John McCrae <john@mccr.ae> for original code
Author: Bernard Bou <1313ou@gmail.com> for rewrite and revamp
"""
#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import unittest

from oewn_xml.wordnet_xml import DashNameFactory, is_valid_xml_id
from tests.model import wn
from tests.utils import collect_entries_for_escapes, print_as_dictionary, generate_senseid_from_sensekey, is_parsable_xml_sensekey, is_valid_xsd_id


class EscapablesTestCase(unittest.TestCase):
    limit = 5

    def test_escapables(self) -> None:
        r = collect_entries_for_escapes(wn.entries, DashNameFactory.char_escapes_for_sk)
        print_as_dictionary(r)
        for k in r:
            v = r[k]
            if v:
                print(f'{k}')
                for i, e in enumerate(r[k]):
                    for s in e.senses:
                        try:
                            sk, esc_sk, unesc_sk = generate_senseid_from_sensekey(s.id)
                            self.assertTrue(is_parsable_xml_sensekey(esc_sk), f'Unparsable {esc_sk}')
                            self.assertTrue(is_valid_xml_id(esc_sk), f'Invalid XML ID {esc_sk}')
                            self.assertTrue(is_valid_xsd_id(esc_sk), f'Invalid xsd:id {esc_sk}')
                            if i < self.limit:
                                print(f'\t{sk} --xml-->  {esc_sk} --reverse-->  {unesc_sk}')
                        except ValueError as ve:
                            self.assertFalse(False, ve)


if __name__ == '__main__':
    unittest.main()
