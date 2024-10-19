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
senses = sorted(list(wn.senses), key=lambda s: s.id)


def is_parsable_sensekey(sk):
    f = sk.split('%')
    if len(f) != 2:
        raise ValueError(f'PERCENT: {sk.id}')

    f2 = f[1].split(':')
    if len(f2) != 5:
        raise ValueError(f'COLON: {sk.id}')
    return True


def is_parsable_xml_sensekey(sk):
    f = sk.split(wordnet_xml.xml_percent_sep)
    if len(f) != 2:
        raise ValueError(f'PERCENT ({wordnet_xml.xml_percent_sep}): {sk.id}')

    f2 = f[1].split(wordnet_xml.xml_colon_sep)
    if len(f2) != 5:
        raise ValueError(f'COLON ({wordnet_xml.xml_colon_sep}): {sk.id}')
    return True


class SensekeysTestCase(unittest.TestCase):

    def test_sensekeys(self):
        for s in senses:
            try:
                self.assertTrue(is_parsable_sensekey(s.id))
                xml_sk = wordnet_xml.escape_sensekey(s.id)
                self.assertTrue(wordnet_xml.is_valid_xml_id(xml_sk))
                self.assertTrue(is_parsable_xml_sensekey(xml_sk))
                sk = wordnet_xml.unescape_sensekey(xml_sk)
                self.assertEqual(s.id, sk)
                print(f'{s.id}   {xml_sk}   {sk}')

            except ValueError as e:
                print(e, file=sys.stderr)


if __name__ == '__main__':
    unittest.main()
