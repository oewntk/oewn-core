"""
WordNet XML ID char validity tests
Author: John McCrae <john@mccr.ae> for original code
Author: Bernard Bou <1313ou@gmail.com> for rewrite and revamp
"""
#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import unittest
from typing import Any, Generator, Tuple

from oewn_xml.wordnet_xml import dash_factory, is_valid_xml_id_char, xml_id_start_char1_re, xml_id_char1_re


def char_range(c1, c2) -> Generator[str, Any, None]:
    """Generates the characters from `c1` to `c2`, inclusive."""
    for c in range(ord(c1), ord(c2) + 1):
        yield chr(c)


def char_ranges(r, ) -> Generator[str, Any, None]:
    for r1, r2 in r:
        for c in char_range(r1, r2):
            yield c


ascii_but_alphanum: Tuple[Tuple[str, str], ...] = (
    ('\x00', '\x2F'),
    ('\x3A', '\x3A'),
    ('\x5F', '\x5F'),
    ('\x7B', '\xBF'),
    # ('\xC0', '\xFF'),
)

printable_ascii_but_alphanum: Tuple[Tuple[str, str], ...] = (
    ('\x20', '\x2F'),
    ('\x3A', '\x3A'),
    ('\x5F', '\x5F'),
    ('\x7B', '\xBF'),
    # ('\xC0', '\xFF'),
)


class XMLIDCharsTestCase(unittest.TestCase):
    def test_ascii_non_letter_range(self) -> None:
        print('\nXML VALID IN ASCII RANGE')
        for c in char_ranges(ascii_but_alphanum):
            start = xml_id_start_char1_re.match(c) is not None
            mid = xml_id_char1_re.match(c) is not None
            if start or mid:
                print(f'{c!r} {ord(c):X} {" start" if start else ''} {"mid" if mid else ''}')
        self.assertTrue(True)

    def test_ascii_invalid_range(self) -> None:
        print('\nESCAPABILITY OF XML INVALID IN ASCII RANGE')
        for c in char_ranges(printable_ascii_but_alphanum):
            if not is_valid_xml_id_char(c):
                is_escaped = c in dash_factory.char_escapes
                print(f'Invalid {c} {c!r} {ord(c):X} {f'ESCAPED AS {dash_factory.char_escapes[c]}' if is_escaped else ''}')
        self.assertTrue(True)

    def test_ascii_diacritics_range(self) -> None:
        print('\nWITH DIACRITICS')
        for c in 'ñéèàâç汉':
            start = is_valid_xml_id_char(c) is not None
            mid = xml_id_char1_re.match(c) is not None
            print(f'{c} {ord(c):X} {" start" if start else ""} {"mid" if mid else ""}')
            self.assertTrue(is_valid_xml_id_char(c))
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
