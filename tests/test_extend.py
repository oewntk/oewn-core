"""
WordNet model extend tests
Author: John McCrae <john@mccr.ae> for original code
Author: Bernard Bou <1313ou@gmail.com> for rewrite and revamp
"""
#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import unittest

from tests.model import wn
from tests.utils import dump


class ExtendTestCase(unittest.TestCase):

    def test_extend(self) -> None:
        s13 = wn.synset_resolver['02372362-v']
        s12 = wn.synset_resolver['00772482-v']
        s11 = wn.synset_resolver['02512195-v']
        s23 = wn.synset_resolver['05544491-n']
        s22 = wn.synset_resolver['05543502-n']
        s21 = wn.synset_resolver['05543117-n']
        print("\nBEFORE EXTEND")
        for s in (s11, s12, s13, s21, s22, s23):
            dump(s)

        wn.extend()

        print("\nAFTER EXTEND")
        for s in (s11, s12, s13, s21, s22, s23):
            dump(s)
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
