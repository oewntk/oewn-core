#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import unittest

from oewn_xml.wordnet_xml import DashNameFactory, escape_sensekey, unescape_sensekey
from tests.utils import collect_entries_for_escapes, print_as_dictionary
from tests.model import wn
from typing import Tuple


def process_sensekey(sk: str) -> Tuple[str, str, str]:
    esc_sk = escape_sensekey(sk)
    unesc_sk = unescape_sensekey(esc_sk)
    if sk != unesc_sk:
        raise ValueError(f'unescaped != original: {sk} != {unesc_sk}')
    return sk, esc_sk, unesc_sk


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
