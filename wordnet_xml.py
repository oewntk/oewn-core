"""
WordNet XML common

Author: John McCrae <john@mccr.ae> for original code
Author: Bernard Bou <1313ou@gmail.com> for rewrite and revamp
"""
#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import re
from typing import Tuple

# Constrain input to avoid non letters or unescaped chars, or not
unconstrained = False

# X M L   I D

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


def escape_lemma(lemma):
    """Escape the lemma so that it contains valid characters for inclusion in XML ID"""

    def escape_char(c):
        if ('A' <= c <= 'Z') or ('a' <= c <= 'z') or ('0' <= c <= '9') or c == '.':
            return c
        elif c == ' ':
            return '_'
        elif c == '(':
            return '-lb-'
        elif c == ')':
            return '-rb-'
        elif c == '\'':
            return '-ap-'
        elif c == '/':
            return '-sl-'
        elif c == ':':
            return '-cn-'
        elif c == ',':
            return '-cm-'
        elif c == '!':
            return '-ex-'
        elif c == '+':
            return '-pl-'
        elif xml_id_char1_re.match(c):  # or xml_id_start_char1_re.match(c):
            return c
        elif unconstrained:
            return f'-{ord(c):04X}-'
        raise ValueError(f'{c!r} [x{ord(c):04X}] is illegal character in XML ID and no escape sequence is defined')

    return ''.join(escape_char(c) for c in lemma)


def unescape_lemma(escaped):
    """Reverse escaping the lemma back to the WN lemma"""
    return (escaped
            .replace('-pl-', '+')
            .replace('-ex-', '!')
            .replace('-cm-', ',')
            .replace('-cn-', ':')
            .replace('-sl-', '/')
            .replace('-ap-', "'")
            .replace('-rb-', ')')
            .replace('-lb-', '(')
            .replace('_', ' '))


def escape_lemma_in_sk(lemma):
    return (lemma
            .replace("'", "-ap-")
            .replace("/", "-sl-")
            .replace("!", "-ex-")
            .replace(",", "-cm-")
            .replace(":", "-cn-")
            .replace("+", "-pl-"))

xml_percent_sep = '__'
xml_colon_sep = '.'

def unescape_lemma_in_sensekey(escaped_lemma):
    return (escaped_lemma
            .replace("-ap-", "'")
            .replace("-sl-", "/")
            .replace("-ex-", "!")
            .replace("-cm-", ",")
            .replace("-cn-", ":")
            .replace("-pl-", "+"))


def escape_sensekey(sensekey):
    """
    Maps a sense key into an OEWN XML form, prefix is added
    """
    if '%' in sensekey:
        e = sensekey.split('%')
        lemma = escape_lemma_in_sk(e[0])
        lex_sense = e[1]
        lex_sense_fields = lex_sense.split(':')
        n = len(lex_sense_fields)
        assert n == 5, f'Parsing error: length {n} of lex_sense_fields in lex_sense {lex_sense} should be 5'
        head = lex_sense_fields[3]
        if head:
            lex_sense_fields[3] = escape_lemma_in_sk(head)
        return f"oewn-{lemma}{xml_percent_sep}{xml_colon_sep.join(lex_sense_fields)}"
    raise ValueError(f'Ill-formed OEWN sense key (no %): {sensekey}')


def unescape_sensekey(escaped_sensekey):
    """
    Unescape an OEWN sense key to a WN sense key
    """
    if xml_percent_sep in escaped_sensekey:
        e = escaped_sensekey.split(xml_percent_sep)
        lemma = unescape_lemma_in_sensekey(e[0])
        lex_sense = e[1]
        lex_sense_fields = lex_sense.split(xml_colon_sep)
        n = len(lex_sense_fields)
        assert n == 5, f'Parsing error: length {n} of lex_sense_fields in lex_sense {lex_sense} should be 5'
        head = lex_sense_fields[3]
        if head:
            lex_sense_fields[3] = unescape_lemma_in_sensekey(head)
        return f'{lemma}%{':'.join(lex_sense_fields)}'
    raise ValueError(f'Ill-formed OEWN sense key (no {xml_percent_sep}): {escaped_sensekey}')


# S Y N S E T / E N T R Y  /  S E N S E   X M L   I D

# Prefix to XML IDs

key_prefix = 'oewn-'
key_prefix_len = len(key_prefix)


def is_valid_xml_oewn_id(_):
    return _.startswith(key_prefix) and is_valid_xml_id(_)


# s y n s e t

def make_synset_id(synsetid: str):
    return f'{key_prefix}{synsetid}'


def unmake_synset_id(xml_synsetid: str):
    return xml_synsetid[key_prefix_len:]


# e n t r y

def make_entry_id(lemma: str, pos: str, discriminant: str | None = None, ):
    p = pos
    d = f'-{discriminant}' if discriminant else ''
    return f'{key_prefix}{escape_lemma(lemma)}-{p}{d}'


def unmake_entry_id(xml_entry_id: str) -> Tuple[str, str, str]:
    entry_id2 = xml_entry_id[key_prefix_len:]
    pos_discriminant = entry_id2[-1]
    if pos_discriminant in ('n', 'v', 'a', 'r'):
        lemma = entry_id2[:-2]
        pos = pos_discriminant
        discriminant = None
    else:
        def penultimate_occurrence(s, char):
            last_index = s.rfind(char)
            if last_index == -1:  # Character not found
                return -1
            return s.rfind(char, 0, last_index)

        cut = penultimate_occurrence(entry_id2, '-')
        if cut == -1:
            raise ValueError(xml_entry_id)
        lemma = entry_id2[:cut]
        pos_discriminant = entry_id2[cut + 1:]
        f = pos_discriminant.split('-')
        pos = f[0]
        discriminant = f[1]
    lemma = unescape_lemma(lemma)
    return lemma, pos, discriminant


# s e n s e

def make_sense_id(sensekey):
    """
    Maps the sensekey so that it contains valid characters for XML ID, prefix added
    :param sensekey: sense key in WN format (YAML)
    :return: sense key in XML format
    """
    return f"{key_prefix}{escape_sensekey(sensekey)}"


def unmake_sense_id(xml_sensekey):
    """
    Maps an OEWN XML sense key back to a WN one
    :param xml_sensekey: sense key in XML format
    :return: sense key in WN format (YAML)
    """
    return unescape_sensekey(xml_sensekey[key_prefix_len:])


# L I T E R A L S

def escape_xml_lit(lit):
    """
    Escape the literal for XML
    :param lit: literal
    :return: escaped literal with escaped entities
    """
    return (lit
            .replace("&", "&amp;")
            .replace("'", "&apos;")
            .replace("\"", "&quot;")
            .replace("<", "&lt;")
            .replace(">", "&gt;"))
