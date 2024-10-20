#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import wordnet_xml


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
        elif wordnet_xml.xml_id_char1_re.match(c):  # or xml_id_start_char1_re.match(c):
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


xml_percent_sep = '__'
xml_colon_sep = '.'


def escape_lemma_in_sk(lemma):
    return (lemma
            .replace("'", "-ap-")
            .replace("/", "-sl-")
            .replace("!", "-ex-")
            .replace(",", "-cm-")
            .replace(":", "-cn-")
            .replace("+", "-pl-"))


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
    Maps a sense key into an OEWN form
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


def unescape_sensekey(sk):
    """
    Maps an OEWN sense key to a WN sense key
    """
    if xml_percent_sep in sk:
        e = sk.split(xml_percent_sep)
        lemma = unescape_lemma_in_sensekey(e[0][wordnet_xml.key_prefix_len:])
        lex_sense = e[1]
        lex_sense_fields = lex_sense.split(xml_colon_sep)
        n = len(lex_sense_fields)
        assert n == 5, f'Parsing error: length {n} of lex_sense_fields in lex_sense {lex_sense} should be 5'
        head = lex_sense_fields[3]
        if head:
            lex_sense_fields[3] = unescape_lemma_in_sensekey(head)
        return f'{lemma}%{':'.join(lex_sense_fields)}'
    raise ValueError(f'Ill-formed OEWN sense key (no {xml_percent_sep}): {sk}')


def make_xml_sensekey(sk):
    esc_sk = escape_sensekey(sk)
    unesc_sk = unescape_sensekey(esc_sk)
    if sk != unesc_sk:
        raise ValueError(f'unescaped != original: {sk} != {unesc_sk}')
    return sk, esc_sk, unesc_sk
