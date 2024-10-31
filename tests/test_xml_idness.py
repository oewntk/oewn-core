"""
WordNet XML ID well-formedness abstract tests
Author: John McCrae <john@mccr.ae> for original code
Author: Bernard Bou <1313ou@gmail.com> for rewrite and revamp
"""
#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import sys
import unittest
from typing import Tuple

from oewn_xml.wordnet_xml import dash_factory, is_valid_xml_id, is_valid_xml_id_char, escape_lemma, unescape_lemma, escape_sensekey, unescape_sensekey


class WordnetXMLTestCase(unittest.TestCase):
    def test_valid_char(self) -> None:
        for c in ('.', '·', ':', '_', '-'):
            self.assertTrue(is_valid_xml_id_char(c), f'Valid {c} {c!r} x{ord(c):X}')
        for c in (',', ';', '%', '!', '?', '*', '/', '|', '\\', '`'):
            self.assertFalse(is_valid_xml_id_char(c), f'Not valid {c} {c!r} x{ord(c):X}')

    def test_valid_ids(self) -> None:
        for s in (
                'a.b',
                'a·b',
                'a:b',
                'a_b',
                'a-b'
        ):
            self.assertTrue(is_valid_xml_id(s), f'Valid {s}')

        for s in (
                'a,b',
                'a;b',
                'a!b',
                'a?b',
                'a*b',
                'a/b',
                'a|b',
                'a\\b',
                'a`b'
        ):
            self.assertFalse(is_valid_xml_id(s), f'Not valid {s}')

    def test_valid_escape_keys(self) -> None:
        d = dash_factory.base_char_escapes
        for c in d:
            self.assertFalse(is_valid_xml_id_char(c), f'Not valid {c} {c!r} x{ord(c):X}')

    def test_valid_escape_unescape_lemmas(self) -> None:
        for l in some_lemmas:
            r = lemma_escape_unescape(l)
            assert r
            l1, l2 = r
            print(f'{l} -> {l1} -> {l2}')
            self.assertTrue(is_valid_xml_id(l1), f'Illegal XML ID "{l1}"')
            self.assertEqual(l, l2, f'Reversing failed {l} {l2}')

    def test_valid_escape_unescape_sensekeys(self) -> None:
        for l in some_lemmas:
            sk = make_yaml_sense_key(l, 1, 2, 3, None, None)
            # sk = 'a_b_c%1:02:03::'
            r = sensekey_escape_unescape(sk)
            assert r
            sk1, sk2 = r
            print(f'{sk} -> {sk1} -> {sk2}')
            self.assertTrue(is_valid_xml_id(sk1), f'Illegal XML ID "{sk1}"')
            self.assertEqual(sk, sk2, f'Reversing failed {sk} {sk2}')


# UTILS

def lemma_escape_unescape(l: str) -> Tuple[str, str] | None:
    try:
        l1 = escape_lemma(l)
        l2 = unescape_lemma(l1)
        return l1, l2
    except ValueError as er:
        print(f'{l} -> LEMMA ERROR {er}', file=sys.stderr)


def sensekey_escape_unescape(sk: str) -> Tuple[str, str] | None:
    try:
        sk1 = escape_sensekey(sk)
        sk2 = unescape_sensekey(sk1)
        return sk1, sk2
    except Exception as er:
        print(f'{sk} -> SENSEKEY ERROR {er}', file=sys.stderr)


def make_yaml_sense_key(lemma: str, ss_type: int, lex_filenum: int, lexid: int, head: str | None,
                        head_id: int | None) -> str:
    """Calculate the sense key for a sense of an entry"""
    lemma2 = lemma.lower().replace(" ", "_").replace("%", "-percent-")
    return f'{lemma2}%{ss_type}:{lex_filenum:02}:{lexid:02}:{head if head is not None else ''}:{f'{head_id:02}' if head_id is not None else ''}'


some_lemmas: Tuple[str, ...] = (
    'protégé',
    'señor',
    'a.b.c',
    'a-b-c',
    'a_b_c',
    'a b c',
    'a:b:c',  # colon
    'a/b/c',
    'a|b|c',
    'a\\b\\c',
    'a,b,c',
    'a;b;c',
    'a=b=c',
    'a+b+c',
    'a(b)c',
    'a{b}c',
    'a[b]c',
    'a!b!c',
    'a?b?c',
    'a$b$c',
    'a#b#c',
    'a%b%c',  # percent
    'a@b@c',
    'a^b^c',
    'a*b*c',
    "a'b'c",
    'a`b`c',
    'a´b´c',
    'a‘quoted’b',
    'a🠀b🠂c',
)

some_illegal_lemmas: Tuple[str, ...] = (
    'a→b←c',
)

some_lemmas_with_percent_or_colon: Tuple[str, ...] = (
    'a%b%c',
    'a:b:c',
)

if __name__ == '__main__':
    unittest.main()
