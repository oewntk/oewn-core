"""
WordNet model transitive validation tests
Author: John McCrae <john@mccr.ae> for original code
Author: Bernard Bou <1313ou@gmail.com> for rewrite and revamp
"""
#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import unittest

import model
import utils
import validate
from oewn_core.wordnet import Synset


class TransitiveTestCase(unittest.TestCase):

    def test_transitive(self):
        s1 = model.wn.synset_resolver['05543117-n']
        # s2 = model.wn.synset_resolver['05543502-n']
        s3 = model.wn.synset_resolver['05544491-n']

        model.wn.extend()

        validate.check_transitive_synset(model.wn, s3)

        print("\nBEFORE EXTEND")
        utils.dump(s3)
        r = Synset.Relation(s1.id, Synset.Relation.Type.HYPERNYM.value)
        s3.relations.append(r)
        print("\nAFTER EXTEND")
        utils.dump(s3)

        with self.assertRaises(validate.ValidationError):
             validate.check_transitive_synset(model.wn, s3)

if __name__ == '__main__':
    unittest.main()
