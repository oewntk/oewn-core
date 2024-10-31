"""
WordNet XML ID discriminant handling tests
Author: John McCrae <john@mccr.ae> for original code
Author: Bernard Bou <1313ou@gmail.com> for rewrite and revamp
"""
#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import unittest

from oewn_xml.wordnet_xml import from_xml_entry_id, to_xml_entry_id


class DiscriminantTestCase(unittest.TestCase):

    def test_discriminant(self) -> None:
        print('\nDISCRIMINANT')
        d1 = '1'
        d2 = '2'
        for lemma in ('bass', 'bow', 'row', 'wind'):
            e_id_0 = to_xml_entry_id(lemma, 'n')
            e_id_1 = to_xml_entry_id(lemma, 'n', d1)
            e_id_2 = to_xml_entry_id(lemma, 'n', d2)
            l_0, p_0, d_0 = from_xml_entry_id(e_id_0)
            l_1, p_1, d_1 = from_xml_entry_id(e_id_1)
            l_2, p_2, d_2 = from_xml_entry_id(e_id_2)
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
