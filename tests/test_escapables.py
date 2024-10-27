#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import unittest

from oewn_xml.wordnet_xml import DashNameFactory
from tests.utils import collect_entries_for_escapes, print_as_dictionary
from tests.model import wn
from tests.utils import process_sensekey


class EscapablesTestCase(unittest.TestCase):
    limit = 5

    def test_escapables(self) -> None:
        r = collect_entries_for_escapes(wn.entries, DashNameFactory.char_escapes_for_sk)
        print_as_dictionary(r)
        for k in r:
            v = r[k]
            if v:
                print(f'{k}')
                for i, e in enumerate(r[k]):
                    for s in e.senses:
                        sk, esc_sk, unesc_sk = process_sensekey(s.id)
                        if i < self.limit:
                            print(f'\t{sk} --xml-->  {esc_sk} --reverse-->  {unesc_sk}')


if __name__ == '__main__':
    unittest.main()
