#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import unittest

import utils
import wordnet_xml as xml
from wordnet_xml import legacy_factory, DashNameFactory


def try_is_valid_xsd_id(_id):
    try:
        utils.is_valid_xsd_id(_id)
        print(f'{_id} is a valid xsd:id')
    except ValueError as ve:
        print(f'{_id} is NOT a valid xsd:id')
        raise ve


class XMLIDCasesTestCase(unittest.TestCase):

    def test_rogue(self):
        print('\nROGUE')
        lemma = 'Capital: Critique of Political Economy'
        sk = 'capital:_critique_of_political_economy%1:10:01::'

        esc_lemma = xml.escape_lemma(lemma)
        xml_entry_id = xml.to_xml_entry_id(lemma, 'n')
        esc_sk = xml.escape_sensekey(sk)
        xml_sense_id = xml.to_xml_sense_id(sk)

        lemma_el = xml.unescape_lemma(esc_lemma)
        lemma_eid, _, _ = xml.from_xml_entry_id(xml_entry_id)
        sk_esk = xml.unescape_sensekey(esc_sk)
        sk_sid = xml.from_xml_sense_id(xml_sense_id)

        print(f'{lemma} --escape_lemma()--> {esc_lemma} --unescape_lemma()--> {lemma_el}')
        print(f'{sk} --escape_sensekey()--> {esc_sk} --unescape_sensekey()--> {sk_esk}')

        print(f'{lemma} --make_entry_id()--> {xml_entry_id} --unmake_entry_id()--> {lemma_eid}')
        print(f'{sk} --make_sense_id()--> {xml_sense_id} --unmake_sense_id()--> {sk_sid}')

        self.assertTrue(xml.is_valid_xml_id(esc_lemma))
        self.assertTrue(xml.is_valid_xml_id(esc_sk))
        self.assertTrue(xml.is_valid_xml_id(xml_entry_id))
        self.assertTrue(xml.is_valid_xml_id(xml_sense_id))

        self.assertTrue(xml.is_valid_xml_oewn_id(xml_entry_id))
        self.assertTrue(xml.is_valid_xml_oewn_id(xml_sense_id))

        self.assertEqual(lemma_el, lemma)
        self.assertEqual(lemma_eid, lemma)
        self.assertEqual(sk_esk, sk)
        self.assertEqual(sk_sid, sk)

    def test_discriminant(self):
        print('\nDISCRIMINANT')
        d1 = '1'
        d2 = '2'
        for lemma in ('bass', 'bow', 'row', 'wind'):
            e_id_0 = xml.to_xml_entry_id(lemma, 'n')
            e_id_1 = xml.to_xml_entry_id(lemma, 'n', d1)
            e_id_2 = xml.to_xml_entry_id(lemma, 'n', d2)
            l_0, p_0, d_0 = xml.from_xml_entry_id(e_id_0)
            l_1, p_1, d_1 = xml.from_xml_entry_id(e_id_1)
            l_2, p_2, d_2 = xml.from_xml_entry_id(e_id_2)
            print(f'{lemma} --entry()--> {e_id_0} --parse--> {l_0} {p_0} {d_0}')
            print(f'{lemma} --entry(1)--> {e_id_1} --parse--> {l_1} {p_1} {d_1}')
            print(f'{lemma} --entry(2)--> {e_id_2} --parse--> {l_2} {p_2} {d_2}')

            self.assertEqual(l_0, lemma)
            self.assertEqual(l_1, lemma)
            self.assertEqual(l_2, lemma)
            self.assertEqual(p_0, 'n')
            self.assertEqual(p_1, 'n')
            self.assertEqual(p_2, 'n')
            self.assertEqual(d_0, None)
            self.assertEqual(d_1, d1)
            self.assertEqual(d_2, d2)

    def test_rogue_xsd_id(self):
        print('\nXSD IDS - ROGUE')
        test_factory = DashNameFactory('__', '.')
        for lemma in ('Capital: Critique of Political Economy',):
            sk = utils.make_dummy_sk(lemma)
            e_id = xml.to_xml_entry_id(lemma, 'n', name_factory=test_factory)
            legacy_e_id = xml.to_xml_entry_id(lemma, 'n', name_factory=legacy_factory)
            sk_id = xml.to_xml_sense_id(sk, name_factory=test_factory)
            legacy_sk_id = xml.to_xml_sense_id(sk, name_factory=legacy_factory)
            print(f'{lemma} -entryid--------> {e_id}')
            print(f'{lemma} -legacy entryid-> {legacy_e_id}')
            print(f'{sk} -senseid--------> {sk_id}')
            print(f'{sk} -legacy senseid-> {legacy_sk_id}')
            print()

            self.assertTrue(xml.is_valid_xml_id(e_id))
            print(f'{e_id} is valid XML ID')
            self.assertTrue(xml.is_valid_xml_id(e_id))
            print(f'{legacy_e_id} is valid XML ID')
            self.assertTrue(xml.is_valid_xml_id(sk_id))
            print(f'{sk_id} is valid XML ID')
            self.assertTrue(xml.is_valid_xml_id(legacy_sk_id))
            print(f'{legacy_sk_id} is valid XML ID')

            self.expect_valid_xsd_id(e_id)
            self.expect_valid_xsd_id(legacy_e_id)
            self.expect_valid_xsd_id(sk_id)
            self.expect_valid_xsd_id(legacy_sk_id)

    def test_xsd_id(self):
        print('\nXSD IDS')
        dummy_colon_id = 'dummy:dummy'
        with self.assertRaises(ValueError, msg=f'{dummy_colon_id} is a valid xsd:id'):
            try_is_valid_xsd_id(dummy_colon_id)
        test_factory = DashNameFactory('__', '.')
        for lemma in ('bass',):
            sk = utils.make_dummy_sk(lemma)
            e_id = xml.to_xml_entry_id(lemma, 'n')
            sk_id = xml.to_xml_sense_id(sk, name_factory=test_factory)
            legacy_sk_id = xml.to_xml_sense_id(sk, name_factory=legacy_factory)
            print(f'{lemma} -entryid-> {e_id}')
            print(f'{sk} -senseid--------> {sk_id}')
            print(f'{sk} -legacy senseid-> {legacy_sk_id}')
            print()

            self.assertTrue(xml.is_valid_xml_id(e_id))
            print(f'{e_id} is valid XML ID')
            self.assertTrue(xml.is_valid_xml_id(sk_id))
            print(f'{sk_id} is valid XML ID')
            self.assertTrue(xml.is_valid_xml_id(legacy_sk_id))
            print(f'legacy {legacy_sk_id} is valid XML ID')

            self.expect_valid_xsd_id(e_id)
            self.expect_valid_xsd_id(sk_id)
            self.expect_valid_xsd_id(legacy_sk_id)

        print()

        for lemma in ('1:1', 'Capital: Critique of Political Economy'):
            sk = utils.make_dummy_sk(lemma)
            e_id = xml.to_xml_entry_id(lemma, 'n')
            sk_id = xml.to_xml_sense_id(sk, name_factory=test_factory)
            legacy_sk_id = xml.to_xml_sense_id(sk, name_factory=legacy_factory)
            print(f'{lemma} -entryid-> {e_id}')
            print(f'{sk} -senseid--------> {sk_id}')
            print(f'{sk} -legacy senseid-> {legacy_sk_id}')
            print()

            self.assertTrue(xml.is_valid_xml_id(e_id))
            print(f'{e_id} is valid XML ID')
            self.assertTrue(xml.is_valid_xml_id(sk_id))
            print(f'{sk_id} is valid XML ID')
            self.assertTrue(xml.is_valid_xml_id(legacy_sk_id))
            print(f'{legacy_sk_id} is valid XML ID')

            self.expect_valid_xsd_id(e_id)
            self.expect_valid_xsd_id(sk_id)
            self.expect_valid_xsd_id(legacy_sk_id)

    def expect_valid_xsd_id(self, _id):
        try_is_valid_xsd_id(_id)
        # print(f'{_id} is valid XML ID')

    def expect_not_valid_xsd_id(self, _id):
        with self.assertRaises(ValueError, msg=f'{_id} is a valid xsd:id'):
            try_is_valid_xsd_id(_id)


if __name__ == '__main__':
    unittest.main()
