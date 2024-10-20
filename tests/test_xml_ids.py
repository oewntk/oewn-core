#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import unittest

import wordnet_xml as xml


def char_range(c1, c2):
    """Generates the characters from `c1` to `c2`, inclusive."""
    for c in range(ord(c1), ord(c2) + 1):
        yield chr(c)


def char_ranges(r, ):
    for r1, r2 in r:
        for c in char_range(r1, r2):
            yield c


ascii_but_alphanum = (
    ('\x00', '\x2F'),
    ('\x3A', '\x3A'),
    ('\x5F', '\x5F'),
    ('\x7B', '\xBF'),
    # ('\xC0', '\xFF'),
)

printable_ascii_but_alphanum = (
    ('\x20', '\x2F'),
    ('\x3A', '\x3A'),
    ('\x5F', '\x5F'),
    ('\x7B', '\xBF'),
    # ('\xC0', '\xFF'),
)


class XMLIDTestCase(unittest.TestCase):
    def test_ascii_non_letter_range(self):
        print('\nXML VALID IN ASCII RANGE')
        for c in char_ranges(ascii_but_alphanum):
            start = xml.xml_id_start_char1_re.match(c) is not None
            mid = xml.xml_id_char1_re.match(c) is not None
            if start or mid:
                print(f'{c!r} {ord(c):X} {" start" if start else ''} {"mid" if mid else ''}')

    def test_ascii_invalid_range(self):
        print('\nESCAPABILITY OF XML INVALID IN ASCII RANGE')
        for c in char_ranges(printable_ascii_but_alphanum):
            if not xml.is_valid_xml_id_char(c):
                is_escaped = c in xml.custom_char_escapes
                print(f'Invalid {c} {c!r} {ord(c):X} {f'ESCAPED AS {xml.custom_char_escapes[c]}' if is_escaped else ''}')
                # self.assertTrue(is_escaped, f'{c!r} {ord(c):X}')

    def test_ascii_diacritics_range(self):
        print('\nWITH DIACRITICS')
        for c in 'ñéèàâç':
            start = xml.is_valid_xml_id_char(c) is not None
            mid = xml.xml_id_char1_re.match(c) is not None
            print(f'{c} {ord(c):X} {" start" if start else ""} {"mid" if mid else ""}')
            self.assertTrue(xml.is_valid_xml_id_char(c))


if __name__ == '__main__':
    unittest.main()
