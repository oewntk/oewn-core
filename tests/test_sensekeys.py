"""
WordNet sensekey tests
Author: John McCrae <john@mccr.ae> for original code
Author: Bernard Bou <1313ou@gmail.com> for rewrite and revamp
"""
#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import sys
import unittest

from oewn_xml.wordnet_xml import is_valid_xml_id, to_xml_sense_id, from_xml_sense_id, key_prefix_len
from tests.model import sorted_senses
from tests.utils import is_parsable_sensekey, is_parsable_xml_sensekey, is_valid_xsd_id


class SensekeysTestCase(unittest.TestCase):

    def test_sensekeys(self) -> None:
        for s in sorted_senses:
            try:
                self.assertTrue(is_parsable_sensekey(s.id))
                sid = to_xml_sense_id(s.id)
                self.assertTrue(is_valid_xml_id(sid), f'{sid}')
                self.assertTrue(is_valid_xsd_id(sid), f'{sid}')
                self.assertTrue(is_parsable_xml_sensekey(sid[key_prefix_len:]), f'{sid}')
                sk = from_xml_sense_id(sid)
                self.assertEqual(s.id, sk)
                print(f'{s.id}   {sid}   {sk}')
            except ValueError as e:
                print(e, file=sys.stderr)


if __name__ == '__main__':
    unittest.main()
