#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import unittest

import wordnet_xml as xml


class XMLIDCasesTestCase(unittest.TestCase):

    def test_rogue(self):
        print('\nROGUE')
        lemma = 'Capital: Critique of Political Economy'
        sk = 'capital:_critique_of_political_economy%1:10:01::'

        esc_lemma = xml.escape_lemma(lemma)
        xml_entry_id = xml.make_entry_id(lemma, 'n')
        esc_sk = xml.escape_sensekey(sk)
        xml_sense_id = xml.make_sense_id(sk)

        lemma_el = xml.unescape_lemma(esc_lemma)
        lemma_eid, _, _ = xml.unmake_entry_id(xml_entry_id)
        sk_esk = xml.unescape_sensekey(esc_sk)
        sk_sid = xml.unmake_sense_id(xml_sense_id)

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
            e_id_0 = xml.make_entry_id(lemma, 'n')
            e_id_1 = xml.make_entry_id(lemma, 'n', d1)
            e_id_2 = xml.make_entry_id(lemma, 'n', d2)
            l_0, p_0, d_0 = xml.unmake_entry_id(e_id_0)
            l_1, p_1, d_1 = xml.unmake_entry_id(e_id_1)
            l_2, p_2, d_2 = xml.unmake_entry_id(e_id_2)
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


if __name__ == '__main__':
    unittest.main()
