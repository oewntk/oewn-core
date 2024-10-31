"""
WordNet model transitive validation tests
When a--hypernym-->b--hypernym-->c, there shouldn't be a--hypernym-->c
Author: John McCrae <john@mccr.ae> for original code
Author: Bernard Bou <1313ou@gmail.com> for rewrite and revamp
"""
#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import unittest

from oewn_core.wordnet import Synset
from oewn_validate.validate import check_transitive_synset, ValidationError
from tests.model import wn
from tests.utils import dump


class TransitiveTestCase(unittest.TestCase):

    def test_transitive(self) -> None:
        s1: Synset = wn.synset_resolver['05543117-n']
        # s2: Synset = wn.synset_resolver['05543502-n']
        s3: Synset = wn.synset_resolver['05544491-n']

        wn.extend()

        check_transitive_synset(wn, s3)

        print("\nBEFORE EXTEND")
        dump(s3)
        r = Synset.Relation(s1.id, Synset.Relation.Type.HYPERNYM.value)
        s3.relations.append(r)
        print("\nAFTER EXTEND")
        dump(s3)

        with self.assertRaises(ValidationError):
            check_transitive_synset(wn, s3)


if __name__ == '__main__':
    unittest.main()
