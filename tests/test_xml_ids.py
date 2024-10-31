"""
WordNet XML ID well-formedness selected cases tests
Author: John McCrae <john@mccr.ae> for original code
Author: Bernard Bou <1313ou@gmail.com> for rewrite and revamp
"""
#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import unittest

from oewn_xml.wordnet_xml import (
    escape_lemma, unescape_lemma, from_xml_entry_id, to_xml_entry_id,
    escape_sensekey, unescape_sensekey, to_xml_sense_id, from_xml_sense_id,
    legacy_factory, DashNameFactory, is_valid_xml_id, is_valid_xml_oewn_id)
from tests.utils import is_valid_xsd_id, make_dummy_sk


def try_is_valid_xsd_id(_id) -> None:
    try:
        is_valid_xsd_id(_id)
        print(f'{_id} is a valid xsd:id')
    except ValueError as ve:
        print(f'{_id} is NOT a valid xsd:id')
        raise ve


class XMLIDTestCase(unittest.TestCase):

    def expect_valid_xsd_id(self, _id) -> None:
        try_is_valid_xsd_id(_id)
        self.assertTrue(True)

    def expect_not_valid_xsd_id(self, _id) -> None:
        with self.assertRaises(ValueError, msg=f'{_id} is a valid xsd:id'):
            try_is_valid_xsd_id(_id)

    def test_rogue(self) -> None:
        print('\nROGUE')
        lemma = 'Capital: Critique of Political Economy'
        sk = 'capital:_critique_of_political_economy%1:10:01::'

        esc_lemma = escape_lemma(lemma)
        xml_entry_id = to_xml_entry_id(lemma, 'n')
        esc_sk = escape_sensekey(sk)
        xml_sense_id = to_xml_sense_id(sk)

        lemma_el = unescape_lemma(esc_lemma)
        lemma_eid, _, _ = from_xml_entry_id(xml_entry_id)
        sk_esk = unescape_sensekey(esc_sk)
        sk_sid = from_xml_sense_id(xml_sense_id)

        print(f'{lemma} --escape_lemma()--> {esc_lemma} --unescape_lemma()--> {lemma_el}')
        print(f'{sk} --escape_sensekey()--> {esc_sk} --unescape_sensekey()--> {sk_esk}')

        print(f'{lemma} --make_entry_id()--> {xml_entry_id} --unmake_entry_id()--> {lemma_eid}')
        print(f'{sk} --make_sense_id()--> {xml_sense_id} --unmake_sense_id()--> {sk_sid}')

        self.assertTrue(is_valid_xml_id(esc_lemma))
        self.assertTrue(is_valid_xml_id(esc_sk))
        self.assertTrue(is_valid_xml_id(xml_entry_id))
        self.assertTrue(is_valid_xml_id(xml_sense_id))

        self.assertTrue(is_valid_xml_oewn_id(xml_entry_id))
        self.assertTrue(is_valid_xml_oewn_id(xml_sense_id))

        self.assertEqual(lemma_el, lemma)
        self.assertEqual(lemma_eid, lemma)
        self.assertEqual(sk_esk, sk)
        self.assertEqual(sk_sid, sk)

    def test_rogue_xsd_id(self) -> None:
        print('\nXSD IDS - ROGUE')
        test_factory = DashNameFactory('__', '.')
        for lemma in ('Capital: Critique of Political Economy',):
            sk = make_dummy_sk(lemma)
            e_id = to_xml_entry_id(lemma, 'n', name_factory=test_factory)
            legacy_e_id = to_xml_entry_id(lemma, 'n', name_factory=legacy_factory)
            sk_id = to_xml_sense_id(sk, name_factory=test_factory)
            legacy_sk_id = to_xml_sense_id(sk, name_factory=legacy_factory)
            print(f'{lemma} -entryid--------> {e_id}')
            print(f'{lemma} -legacy entryid-> {legacy_e_id}')
            print(f'{sk} -senseid--------> {sk_id}')
            print(f'{sk} -legacy senseid-> {legacy_sk_id}')
            print()

            self.assertTrue(is_valid_xml_id(e_id))
            print(f'{e_id} is valid XML ID')
            self.assertTrue(is_valid_xml_id(e_id))
            print(f'{legacy_e_id} is valid XML ID')
            self.assertTrue(is_valid_xml_id(sk_id))
            print(f'{sk_id} is valid XML ID')
            self.assertTrue(is_valid_xml_id(legacy_sk_id))
            print(f'{legacy_sk_id} is valid XML ID')

            self.expect_valid_xsd_id(e_id)
            self.expect_valid_xsd_id(legacy_e_id)
            self.expect_valid_xsd_id(sk_id)
            self.expect_valid_xsd_id(legacy_sk_id)

    def test_xsd_id(self) -> None:
        print('\nXSD IDS')
        dummy_colon_id = 'dummy:dummy'
        with self.assertRaises(ValueError, msg=f'{dummy_colon_id} is a valid xsd:id'):
            try_is_valid_xsd_id(dummy_colon_id)
        test_factory = DashNameFactory('__', '.')
        for lemma in ('bass',):
            sk = make_dummy_sk(lemma)
            e_id = to_xml_entry_id(lemma, 'n')
            sk_id = to_xml_sense_id(sk, name_factory=test_factory)
            legacy_sk_id = to_xml_sense_id(sk, name_factory=legacy_factory)
            print(f'{lemma} -entryid-> {e_id}')
            print(f'{sk} -senseid--------> {sk_id}')
            print(f'{sk} -legacy senseid-> {legacy_sk_id}')
            print()

            self.assertTrue(is_valid_xml_id(e_id))
            print(f'{e_id} is valid XML ID')
            self.assertTrue(is_valid_xml_id(sk_id))
            print(f'{sk_id} is valid XML ID')
            self.assertTrue(is_valid_xml_id(legacy_sk_id))
            print(f'legacy {legacy_sk_id} is valid XML ID')

            self.expect_valid_xsd_id(e_id)
            self.expect_valid_xsd_id(sk_id)
            self.expect_valid_xsd_id(legacy_sk_id)

        print()

        for lemma in ('1:1', 'Capital: Critique of Political Economy'):
            sk = make_dummy_sk(lemma)
            e_id = to_xml_entry_id(lemma, 'n')
            sk_id = to_xml_sense_id(sk, name_factory=test_factory)
            legacy_sk_id = to_xml_sense_id(sk, name_factory=legacy_factory)
            print(f'{lemma} -entryid-> {e_id}')
            print(f'{sk} -senseid--------> {sk_id}')
            print(f'{sk} -legacy senseid-> {legacy_sk_id}')
            print()

            self.assertTrue(is_valid_xml_id(e_id))
            print(f'{e_id} is valid XML ID')
            self.assertTrue(is_valid_xml_id(sk_id))
            print(f'{sk_id} is valid XML ID')
            self.assertTrue(is_valid_xml_id(legacy_sk_id))
            print(f'{legacy_sk_id} is valid XML ID')

            self.expect_valid_xsd_id(e_id)
            self.expect_valid_xsd_id(sk_id)
            self.expect_valid_xsd_id(legacy_sk_id)


if __name__ == '__main__':
    unittest.main()
