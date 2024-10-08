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

# Regular expressions for valid NameStartChar and NameChar based on the XML 1.0 specification.
# based on the XML 1.0 specification.
# We don't check for 1st character extra restrictions
# because it's always prefixed with 'oewn-'
xml_id_az = r'A-Za-z'
xml_id_num = r'0-9'
xml_id_extend = (
    r'\xC0-\xD6'  # ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ
    r'\xD8-\xF6'  # ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö
    r'\xF8-\u02FF'
    r'\u0370-\u037D'
    r'\u037F-\u1FFF'
    r'\u200C-\u200D'
    r'\u2070-\u218F'
    r'\u2C00-\u2FEF'
    r'\u3001-\uD7FF'
    r'\uF900-\uFDCF'
    r'\uFDF0-\uFFFD'
)
xml_id_not_first = (
    r'\u0300-\u036F'
    r'\u203F-\u2040'
)
xml_id_start_char = fr'[_{xml_id_az}{xml_id_extend}]' # not used if oewn- prefix
xml_id_start_char1 = fr'^{xml_id_start_char}$'
xml_id_start_char1_re = re.compile(xml_id_start_char)

xml_id_char = fr'[_\-\.·{xml_id_az}{xml_id_num}{xml_id_extend}{xml_id_not_first}]' # + hyphen, stop, midpoint, digits, extras
xml_id_char1 = fr'^{xml_id_char}$'
xml_id_char1_re = re.compile(xml_id_char1)

def escape_xml_lit(lit):
    return (lit
            .replace("&", "&amp;")
            .replace("'", "&apos;")
            .replace("\"", "&quot;")
            .replace("<", "&lt;")
            .replace(">", "&gt;"))


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
        elif xml_id_char1_re.match(c): # or xml_id_start_char1_re.match(c):
            return c
        raise ValueError(f'Illegal character {c}')

    return "".join(escape_char(c) for c in lemma)


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


def escape_sensekey(sensekey):
    """Escape the sensekey so that it contains valid characters for XML ID, prefix added"""
    if "%" in sensekey:
        e = sensekey.split("%")
        return (key_prefix +
                e[0]
                .replace("'", "-ap-")
                .replace("/", "-sl-")
                .replace("!", "-ex-")
                .replace(",", "-cm-")
                .replace(":", "-cn-")
                .replace("+", "-pl-") +
                "__" +
                e[1]
                .replace("_", "-sp-")
                .replace(":", "."))
    else:
        return (key_prefix +
                sensekey
                .replace("%", "__")
                .replace("'", "-ap-")
                .replace("/", "-sl-")
                .replace("!", "-ex-")
                .replace(",", "-cm-")
                .replace(":", "-cn-")
                .replace("+", "-pl-"))


def unescape_sensekey(escaped):
    """Reverse the escaping of a sensekey to a WN sensekey, prefix stripped"""
    if "__" in escaped:
        e = escaped.split("__")
        l = e[0][key_prefix_len:]
        r = "__".join(e[1:])
        return (l
                .replace("-ap-", "'")
                .replace("-sl-", "/")
                .replace("-ex-", "!")
                .replace("-cm-", ",")
                .replace("-cn-", ":")
                .replace("-pl-", "+") +
                "%" +
                r
                .replace(".", ":")
                .replace("-sp-", "_"))
    else:
        return (escaped[key_prefix_len:]
                .replace("__", "%")
                .replace("-ap-", "'")
                .replace("-sl-", "/")
                .replace("-ex-", "!")
                .replace("-cm-", ",")
                .replace("-cn-", ":")
                .replace("-pl-", "+"))
