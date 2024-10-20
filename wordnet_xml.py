"""
WordNet XML common

Author: John McCrae <john@mccr.ae> for original code
Author: Bernard Bou <1313ou@gmail.com> for rewrite and revamp
"""
#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import re

key_prefix = 'oewn-'

key_prefix_len = len(key_prefix)

# Regular expressions for valid NameStartChar and NameChar based on the XML 1.1 specification.
# based on the XML 1.0 specification.
# We don't check for 1st character extra restrictions
# because it's always prefixed with 'oewn-'
xml_id_punct = r':_'  # colon, underscore
xml_id_punct_not_first = r'\-\.·'  # hyphen-minus, period, middle dot
xml_id_az = r'A-Za-z'
xml_id_num = r'0-9'
xml_id_extend = (
    r'\xC0-\xD6'  # Latin letters with diacritics
    r'\xD8-\xF6'  # Additional latin letters with diacritics
    r'\xF8-\u02FF'  # Extended Latin letters and characters from the Latin Extended-A, Greek, and other blocks
    r'\u0370-\u037D'  # Greek letters and many characters from scripts such as Coptic, Armenian, Hebrew, Arabic, and more
    r'\u037F-\u1FFF'  # Greek letters and many characters from scripts such as Coptic, Armenian, Hebrew, Arabic, and more
    r'\u200C-\u200D'  # Zero Width Non-Joiner (ZWNJ) and Zero Width Joiner (ZWJ), used in scripts like Arabic and Indic.
    r'\u2070-\u218F'  # Superscripts, subscripts, and various other symbols.
    r'\u2C00-\u2FEF'  # Characters from the Glagolitic and other historical scripts.
    r'\u3001-\uD7FF'  # Characters from many Asian scripts, including Chinese, Japanese, and Korean ideographs
    r'\uF900-\uFDCF'  # Compatibility ideographs and Arabic presentation forms
    r'\uFDF0-\uFFFD'  # Compatibility ideographs and Arabic presentation forms
    r'\U00010000-\U000EFFFF'
    # Supplementary chars from planes outside the Basic Multilingual Plane, including rare historical scripts, musical symbols, emoji, and more.
)
xml_id_extend_not_first = (
    r'\u0300-\u036F'  # Combining diacritical marks that can modify the preceding character.
    r'\u203F-\u2040'  # Characters like the "undertie" (‿) and "character tie" (⁀), used in specialized phonetic notations.
)
xml_id_start_char = fr'[{xml_id_punct}{xml_id_az}{xml_id_extend}]'  # not used if oewn- prefix
xml_id_char = fr'[{xml_id_punct}{xml_id_punct_not_first}{xml_id_az}{xml_id_num}{xml_id_extend}{xml_id_extend_not_first}]'

xml_id_start_char1 = fr'^{xml_id_start_char}$'
xml_id_char1 = fr'^{xml_id_char}$'

xml_id_start_char1_re = re.compile(xml_id_start_char1)
xml_id_char1_re = re.compile(xml_id_char1)

xml_id = fr'^{xml_id_start_char}{xml_id_char}*$'
xml_id_re = re.compile(xml_id)


def is_valid_xml_id_char(c):
    return xml_id_char1_re.match(c) is not None


def is_valid_xml_id(s):
    return xml_id_re.match(s) is not None


custom_esc_char_escapes = {
    '-': '--',  # custom
}
custom_base_char_escapes = {
    # HTML entities
    # https://en.wikipedia.org/wiki/List_of_XML_and_HTML_character_entity_references
    "'": '-apos-',
    '`': '-grave-',
    '´': '-acute-',
    '‘': '-lsquo-',
    '’': '-rsquo-',
    '(': '-lpar-',
    ')': '-rpar-',
    '[': '-lsqb-',
    ']': '-rsqb-',
    '{': '-lbrace-',
    '}': '-rbrace-',
    ',': '-comma-',
    ';': '-semi-',
    '=': '-equals-',
    '+': '-plus-',
    '!': '-excl-',
    '?': '-quest-',
    '@': '-commat-',
    '#': '-num-',
    '%': '-percnt-',
    '&': '-amp-',
    '§': '-sect-',
    '¶': '-para-',
    '/': '-sol-',
    '\\': '-bsol-',
    '|': '-vert-',
    '^': '-Hat-',
    '*': '-ast-',
    '$': '-dollar-',
    '¢': '-cent-',
    '£': '-pound-',
    '©': '-copy-',
    '®': '-reg-',
    'º': '-ordm-',
    '°': '-deg-',
    '~': '-tilde-',
    '': '--',
    '': '--',
    '': '--',
    '': '--',
    '': '--',
    '': '--',
    '': '--',
    '': '--',
    '': '--',
    '': '--',
    '': '--',
}
custom_extras_char_escapes = {
    '_': '-lowbar-',
    ' ': '_',
}
custom_sk_char_escapes = {
    '-': '--',  # custom
}

custom_char_escapes = custom_esc_char_escapes | custom_base_char_escapes | custom_extras_char_escapes
custom_char_escapes_reverse = {custom_char_escapes[k]: k for k in custom_char_escapes}

custom_char_escapes_for_sk = custom_base_char_escapes | custom_sk_char_escapes
custom_char_escapes_for_sk_reverse = {custom_char_escapes_for_sk[k]: k for k in custom_char_escapes_for_sk}


def escape_lemma(lemma):
    """Format the lemma so it is valid XML ID sequence"""

    def elc(c):
        if ('A' <= c <= 'Z') or ('a' <= c <= 'z') or ('0' <= c <= '9'):
            return c
        elif c in custom_char_escapes:
            return custom_char_escapes[c]
        elif xml_id_char1_re.match(c):
            return c
        raise ValueError(f'{c!r} [x{ord(c):04X}] is illegal character in XML ID and no escape sequence is defined')

    return ''.join(elc(c) for c in lemma)


def unescape_lemma(lemma):
    """
    Unformat the valid XML ID sequence so it is the original lemma
    Reversing the keys matters.
    """

    s = lemma
    for seq in reversed(custom_char_escapes_reverse):
        s = s.replace(seq, custom_char_escapes_reverse[seq])
    return s


def escape_lemma_for_sk(lemma):
    """Format the lemma so it is valid XML ID sequence"""

    def elc(c):
        if ('A' <= c <= 'Z') or ('a' <= c <= 'z') or ('0' <= c <= '9'):
            return c
        elif c in custom_char_escapes_for_sk:
            return custom_char_escapes_for_sk[c]
        elif xml_id_char1_re.match(c):
            return c
        raise ValueError(f'{c!r} [x{ord(c):04X}] is illegal character in XML ID and no escape sequence is defined')

    return ''.join(elc(c) for c in lemma)


def unescape_lemma_for_sk(lemma):
    """Format the valid XML ID sequence so it is the original lemma"""
    s = lemma
    for seq in custom_char_escapes_for_sk_reverse:
        s = s.replace(seq, custom_char_escapes_for_sk_reverse[seq])
    return s


middledot = '·'
xml_percent_sep = middledot
xml_colon_sep = ':'


def escape_sensekey(sensekey):
    """Escape the sensekey so that it contains valid characters for XML ID, prefix added"""
    if '%' in sensekey:
        e = sensekey.split('%')
        lemma = escape_lemma_for_sk(e[0])
        lex_sense = e[1]
        lex_sense_fields = lex_sense.split(':')
        n = len(lex_sense_fields)
        assert n == 5, f'Parsing error: length {n} of lex_sense_fields in lex_sense {lex_sense} should be 5'
        head = lex_sense_fields[3]
        if head:
            lex_sense_fields[3] = escape_lemma_for_sk(head)
        return f"oewn-{lemma}{xml_percent_sep}{xml_colon_sep.join(lex_sense_fields)}"
    raise ValueError(f'Ill-formed OEWN sense key (no %): {sensekey}')


def unescape_sensekey(escaped_sensekey):
    """
    Maps an OEWN sense key to a WN sense key
    """
    if xml_percent_sep in escaped_sensekey:
        e = escaped_sensekey.split(xml_percent_sep)
        lemma = unescape_lemma_for_sk(e[0][key_prefix_len:])
        lex_sense = e[1]
        lex_sense_fields = lex_sense.split(xml_colon_sep)
        n = len(lex_sense_fields)
        assert n == 5, f'Parsing error: length {n} of lex_sense_fields in lex_sense {lex_sense} should be 5'
        head = lex_sense_fields[3]
        if head:
            lex_sense_fields[3] = unescape_lemma_for_sk(head)
        return f'{lemma}%{':'.join(lex_sense_fields)}'
    raise ValueError(f'Ill-formed OEWN sense key (no {xml_percent_sep}): {escaped_sensekey}')


def escape_xml_lit(lit):
    return (lit
            .replace("&", "&amp;")
            .replace("'", "&apos;")
            .replace("\"", "&quot;")
            .replace("<", "&lt;")
            .replace(">", "&gt;"))
