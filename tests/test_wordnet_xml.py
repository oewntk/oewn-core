#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import unittest

from wordnet_xml import is_valid_xml_id, is_valid_xml_id_char


class XMLTestCase(unittest.TestCase):
    def test_valid_char(self):
        for c in ('.', '·', ':', '_', '-'):
            self.assertTrue(is_valid_xml_id_char(c), f'Valid {c} {c!r} x{ord(c):X}')
        for c in (',', ';', '%', '!', '?', '*', '/', '|', '\\', '`'):
            self.assertFalse(is_valid_xml_id_char(c), f'Not valid {c} {c!r} x{ord(c):X}')

    def test_valid_ids(self):
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


if __name__ == '__main__':
    unittest.main()
