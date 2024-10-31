"""
WordNet XML common

Author: John McCrae <john@mccr.ae> for original code
Author: Bernard Bou <1313ou@gmail.com> for rewrite and revamp
Author: Michael Wayne Goodman <goodman.m.w@gmail.com> for escaping
"""
#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import re
from abc import abstractmethod, ABC
from typing import Any, Dict, Tuple

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

xml_id_start_char1_re: re.Pattern[str] = re.compile(xml_id_start_char1)
xml_id_char1_re: re.Pattern = re.compile(xml_id_char1)

xml_id = fr'^{xml_id_start_char}{xml_id_char}*$'
xml_id_re: re.Pattern = re.compile(xml_id)


# V A L I D I T Y

def is_valid_xml_id_char(c) -> bool:
    return bool(xml_id_char1_re.match(c))


def is_valid_xml_id(s) -> bool:
    return bool(xml_id_re.match(s))


# E S C A P I N G

def split_at_last(s, c) -> Tuple[Any, Any]:
    cut = s.rfind(c)
    if cut > -1:
        return s[:cut], s[cut + len(c):]
    raise ValueError(f'"{s}" to be cut at last "{c}"')


class NameFactory(ABC):
    """
    Abstract Base Class / Interface
    """

    @abstractmethod
    def escape_lemma(self, lemma: str) -> str:
        pass

    @abstractmethod
    def unescape_lemma(self, esc_lemma: str) -> str:
        pass

    @abstractmethod
    def escape_sensekey(self, sensekey: str) -> str:
        pass

    @abstractmethod
    def unescape_sensekey(self, esc_sensekey: str) -> str:
        pass


class LegacyNameFactory(NameFactory):
    def escape_lemma(self, lemma) -> str:
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
            raise ValueError(f'Illegal character {c}')

        return "".join(escape_char(c) for c in lemma)

    def unescape_lemma(self, esc_lemma):
        """Reverse escaping the lemma back to the WN lemma"""
        return (esc_lemma
                .replace('-pl-', '+')
                .replace('-ex-', '!')
                .replace('-cm-', ',')
                .replace('-cn-', ':')
                .replace('-sl-', '/')
                .replace('-ap-', "'")
                .replace('-rb-', ')')
                .replace('-lb-', '(')
                .replace('_', ' '))

    xml_percent_sep = '__'
    xml_colon_sep = '.'

    def escape_sensekey(self, sensekey) -> str:
        """
        Maps a sense key into an OEWN form
        """

        def escape_lemma_in_sensekey(lemma):
            return (lemma
                    .replace("'", "-ap-")
                    .replace("/", "-sl-")
                    .replace("!", "-ex-")
                    .replace(",", "-cm-")
                    .replace(":", "-cn-")
                    .replace("+", "-pl-"))

        if '%' in sensekey:
            l, lex_sense = split_at_last(sensekey, '%')
            esc_lemma = escape_lemma_in_sensekey(l)
            lex_sense_fields = lex_sense.split(':')
            n = len(lex_sense_fields)
            assert n == 5, f'Parsing error: length {n} of lex_sense_fields in lex_sense {lex_sense} should be 5'
            head = lex_sense_fields[3]
            if head:
                lex_sense_fields[3] = escape_lemma_in_sensekey(head)
            return f"{esc_lemma}{self.xml_percent_sep}{self.xml_colon_sep.join(lex_sense_fields)}"
        raise ValueError(f'Ill-formed OEWN sense key (no %): {sensekey}')

    def unescape_sensekey(self, esc_sensekey) -> str:
        """
        Maps an OEWN sense key to a WN sense key
        """

        def unescape_lemma_in_sensekey(esc_lemma):
            return (esc_lemma
                    .replace("-ap-", "'")
                    .replace("-sl-", "/")
                    .replace("-ex-", "!")
                    .replace("-cm-", ",")
                    .replace("-cn-", ":")
                    .replace("-pl-", "+"))

        if self.xml_percent_sep in esc_sensekey:
            l, lex_sense = split_at_last(esc_sensekey, self.xml_percent_sep)
            lemma = unescape_lemma_in_sensekey(l)
            lex_sense_fields = lex_sense.split(self.xml_colon_sep)
            n = len(lex_sense_fields)
            assert n == 5, f'Parsing error: length {n} of lex_sense_fields in lex_sense {lex_sense} should be 5'
            head = lex_sense_fields[3]
            if head:
                lex_sense_fields[3] = unescape_lemma_in_sensekey(head)
            return f'{lemma}%{':'.join(lex_sense_fields)}'
        raise ValueError(f'Ill-formed OEWN sense key (no {self.xml_percent_sep}): {esc_sensekey}')


class DashNameFactory(NameFactory):
    esc_char_escapes: Dict[str, str] = {
        '-': '--',  # custom
    }
    base_char_escapes: Dict[str, str] = {
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
    }
    extra_char_escapes: Dict[str, str] = {
        '_': '-lowbar-',
        ' ': '_',
        ':': '-colon-',  # to make valid xsd:ids otherwise not necessary for XML:IDs
    }
    sk_char_escapes: Dict[str, str] = {
        '-': '--',
        ':': '-colon-',  # to make valid xsd:ids otherwise not necessary for XML:IDs
    }

    char_escapes: Dict[str, str] = esc_char_escapes | base_char_escapes | extra_char_escapes
    char_escapes_reverse: Dict[str, str] = {v: k for k, v in char_escapes.items()}

    char_escapes_for_sk: Dict[str, str] = base_char_escapes | sk_char_escapes
    char_escapes_for_sk_reverse: Dict[str, str] = {v: k for k, v in char_escapes_for_sk.items()}

    def __init__(self, main_separator, minor_separator) -> None:
        self.xml_percent_sep = main_separator
        self.xml_colon_sep = minor_separator

    # l e m m a

    def escape_lemma(self, lemma) -> str:
        """
        Escape the lemma so that it contains only valid characters for inclusion in XML ID
        """

        def escape_char(c):
            if ('A' <= c <= 'Z') or ('a' <= c <= 'z') or ('0' <= c <= '9'):
                return c
            elif c in self.char_escapes:
                return self.char_escapes[c]
            elif xml_id_char1_re.match(c):
                return c
            elif unconstrained:
                return f'-{ord(c):04X}-'
            raise ValueError(f'{c!r} [x{ord(c):04X}] is illegal character in XML ID and no escape sequence is defined')

        return ''.join(escape_char(c) for c in lemma)

    def unescape_lemma(self, esc_lemma):
        """
        Reverse the escaping and retrieve the original lemma
        Reversing the keys matters because application order matters
        """

        s = esc_lemma
        for seq in reversed(self.char_escapes_reverse.keys()):
            s = s.replace(seq, self.char_escapes_reverse[seq])
        return s

    # s e n s e k e y

    def escape_lemma_in_sensekey(self, lemma) -> str:
        """
        Escape the lemma so that it contains only valid characters for inclusion in XML ID
        within the context of sense id factory
        """

        def escape_char(c):
            if ('A' <= c <= 'Z') or ('a' <= c <= 'z') or ('0' <= c <= '9'):
                return c
            elif c in self.char_escapes_for_sk:
                return self.char_escapes_for_sk[c]
            elif xml_id_char1_re.match(c):
                return c
            elif unconstrained:
                return f'-{ord(c):04X}-'
            raise ValueError(f'{c!r} [x{ord(c):04X}] is illegal character in XML ID and no escape sequence is defined')

        return ''.join(escape_char(c) for c in lemma)

    def unescape_lemma_in_sensekey(self, esc_lemma):
        """
        Reverse the escaping and retrieve the original lemma
        within the context of sense id factory
        """
        s = esc_lemma
        for seq in self.char_escapes_for_sk_reverse:
            s = s.replace(seq, self.char_escapes_for_sk_reverse[seq])
        return s

    def escape_sensekey(self, sensekey) -> str:
        """Escape the sensekey so that it contains valid characters for XML ID"""
        if '%' in sensekey:
            l, lex_sense = split_at_last(sensekey, '%')
            lemma = self.escape_lemma_in_sensekey(l)
            lex_sense_fields = lex_sense.split(':')
            n = len(lex_sense_fields)
            assert n == 5, f'Parsing error: length {n} of lex_sense_fields in lex_sense {lex_sense} should be 5'
            head = lex_sense_fields[3]
            if head:
                lex_sense_fields[3] = self.escape_lemma_in_sensekey(head)
            return f"{lemma}{self.xml_percent_sep}{self.xml_colon_sep.join(lex_sense_fields)}"
        raise ValueError(f'Ill-formed OEWN sense key (no %): {sensekey}')

    def unescape_sensekey(self, esc_sensekey) -> str:
        """
        Unescape an OEWN sense key to a WN sense key
        """
        if self.xml_percent_sep in esc_sensekey:
            l, lex_sense = split_at_last(esc_sensekey, self.xml_percent_sep)
            lemma = self.unescape_lemma_in_sensekey(l)
            lex_sense_fields = lex_sense.split(self.xml_colon_sep)
            n = len(lex_sense_fields)
            assert n == 5, f'Parsing error: length {n} of lex_sense_fields in lex_sense {lex_sense} should be 5'
            head = lex_sense_fields[3]
            if head:
                lex_sense_fields[3] = self.unescape_lemma_in_sensekey(head)
            return f'{lemma}%{':'.join(lex_sense_fields)}'
        raise ValueError(f'Ill-formed OEWN sense key (no {self.xml_percent_sep}): {esc_sensekey}')


# S Y N S E T / E N T R Y  /  S E N S E   X M L   I D

# Name factory

legacy_factory: LegacyNameFactory = LegacyNameFactory()
middledot = '·'
dash_factory: DashNameFactory = DashNameFactory(middledot, '.')
default_factory: NameFactory = dash_factory


def escape_lemma(lemma) -> str:
    return default_factory.escape_lemma(lemma)


def unescape_lemma(esc_lemma) -> str:
    return default_factory.unescape_lemma(esc_lemma)


def escape_sensekey(sensekey) -> str:
    return default_factory.escape_sensekey(sensekey)


def unescape_sensekey(esc_sensekey) -> str:
    return default_factory.unescape_sensekey(esc_sensekey)


# Prefix to XML IDs

key_prefix = 'oewn-'
key_prefix_len = len(key_prefix)


def is_valid_xml_oewn_id(_):
    return _.startswith(key_prefix) and is_valid_xml_id(_)


# s y n s e t

def to_xml_synset_id(synsetid: str) -> str:
    return f'{key_prefix}{synsetid}'


def from_xml_synset_id(xml_synsetid: str) -> str:
    return xml_synsetid[key_prefix_len:]


# e n t r y

def to_xml_entry_id(lemma: str, pos: str, discriminant: str | None = None, name_factory=default_factory):
    p = pos
    d = f'-{discriminant}' if discriminant else ''
    return f'{key_prefix}{name_factory.escape_lemma(lemma)}-{p}{d}'


def from_xml_entry_id(xml_entry_id: str, name_factory=default_factory) -> Tuple[str, str, str | None]:
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
    lemma = name_factory.unescape_lemma(lemma)
    return lemma, pos, discriminant


# s e n s e

def to_xml_sense_id(sensekey, name_factory=default_factory) -> str:
    """
    Maps the sensekey so that it contains valid characters for XML ID, prefix added
    :param sensekey: sense key in WN format (YAML)
    :param name_factory: name factory used
    :return: sense key in XML format
    """
    return f"{key_prefix}{name_factory.escape_sensekey(sensekey)}"


def from_xml_sense_id(xml_sensekey, name_factory=default_factory):
    """
    Maps an OEWN XML sense key back to a WN one
    :param xml_sensekey: sense key in XML format
    :param name_factory: name factory used
    :return: sense key in WN format (YAML)
    """
    return name_factory.unescape_sensekey(xml_sensekey[key_prefix_len:])


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
