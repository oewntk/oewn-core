#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import sys
import unittest

import model
import wordnet_xml as xml
from wordnet_xml import key_prefix_len


def is_parsable_sensekey(sk):
    f = sk.split('%')
    if len(f) != 2:
        raise ValueError(f'PERCENT: {sk.id}')

    f2 = f[1].split(':')
    if len(f2) != 5:
        raise ValueError(f'COLON: {sk.id}')
    return True


def is_parsable_xml_sensekey(sk):
    f = sk.split(xml.xml_percent_sep)
    if len(f) != 2:
        raise ValueError(f'PERCENT ({xml.xml_percent_sep}): {sk}')

    f2 = f[1].split(xml.xml_colon_sep)
    if len(f2) != 5:
        raise ValueError(f'COLON ({xml.xml_colon_sep}): {sk}')
    return True


class SensekeysTestCase(unittest.TestCase):

    def test_sensekeys(self):
        for s in model.sorted_senses:
            try:
                self.assertTrue(is_parsable_sensekey(s.id))
                sid = xml.make_sense_id(s.id)
                self.assertTrue(xml.is_valid_xml_id(sid), f'{sid}')
                self.assertTrue(is_parsable_xml_sensekey(sid[key_prefix_len:]), f'{sid}')
                sk = xml.unmake_sense_id(sid)
                self.assertEqual(s.id, sk)
                print(f'{s.id}   {sid}   {sk}')

            except ValueError as e:
                print(e, file=sys.stderr)


if __name__ == '__main__':
    unittest.main()
