#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import unittest

import test_escapables
import wordnet_xml


def legacy_escape_lemma(lemma):
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


def legacy_unescape_lemma(escaped):
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


legacy_xml_percent_sep = '__'
legacy_xml_colon_sep = '.'


def legacy_escape_lemma_in_sk(lemma):
    return (lemma
            .replace("'", "-ap-")
            .replace("/", "-sl-")
            .replace("!", "-ex-")
            .replace(",", "-cm-")
            .replace(":", "-cn-")
            .replace("+", "-pl-"))


def legacy_unescape_lemma_in_sensekey(escaped_lemma):
    return (escaped_lemma
            .replace("-ap-", "'")
            .replace("-sl-", "/")
            .replace("-ex-", "!")
            .replace("-cm-", ",")
            .replace("-cn-", ":")
            .replace("-pl-", "+"))


def legacy_escape_sensekey(sensekey):
    """
    Maps a sense key into an OEWN form
    """
    if '%' in sensekey:
        e = sensekey.split('%')
        lemma = legacy_escape_lemma_in_sk(e[0])
        lex_sense = e[1]
        lex_sense_fields = lex_sense.split(':')
        n = len(lex_sense_fields)
        assert n == 5, f'Parsing error: length {n} of lex_sense_fields in lex_sense {lex_sense} should be 5'
        head = lex_sense_fields[3]
        if head:
            lex_sense_fields[3] = legacy_escape_lemma_in_sk(head)
        return f"oewn-{lemma}{legacy_xml_percent_sep}{legacy_xml_colon_sep.join(lex_sense_fields)}"
    raise ValueError(f'Ill-formed OEWN sense key (no %): {sensekey}')


def legacy_unescape_sensekey(sk):
    """
    Maps an OEWN sense key to a WN sense key
    """
    if legacy_xml_percent_sep in sk:
        e = sk.split(legacy_xml_percent_sep)
        lemma = legacy_unescape_lemma_in_sensekey(e[0][wordnet_xml.key_prefix_len:])
        lex_sense = e[1]
        lex_sense_fields = lex_sense.split(legacy_xml_colon_sep)
        n = len(lex_sense_fields)
        assert n == 5, f'Parsing error: length {n} of lex_sense_fields in lex_sense {lex_sense} should be 5'
        head = lex_sense_fields[3]
        if head:
            lex_sense_fields[3] = legacy_unescape_lemma_in_sensekey(head)
        return f'{lemma}%{':'.join(lex_sense_fields)}'
    raise ValueError(f'Ill-formed OEWN sense key (no {legacy_xml_percent_sep}): {sk}')


def process_sensekey(sk):
    esc_sk = legacy_escape_sensekey(sk)
    unesc_sk = legacy_unescape_sensekey(esc_sk)
    if sk != unesc_sk:
        raise ValueError(f'unescaped != original: {sk} != {unesc_sk}')
    return sk, esc_sk, unesc_sk


def compare_xml_sensekeys(sk):
    esc_sk = wordnet_xml.escape_sensekey(sk)
    legacy_esc_sk = legacy_escape_sensekey(sk)
    return sk, esc_sk, legacy_esc_sk


class EscapeSchemesTestCase(unittest.TestCase):
    limit = 5

    def test_escapables(self):
        r = test_escapables.collect_entries_for_escapes(test_escapables.entries, wordnet_xml.custom_char_escapes_for_sk)
        for k in r:
            v = r[k]
            if v:
                print(f'{k}')
                for i, e in enumerate(r[k]):
                    for s in e.senses:
                        sk, esc_sk, unesc_sk = process_sensekey(s.id)
                        if i < self.limit:
                            print(f'\t{sk} --xml-->  {esc_sk} --reverse-->  {unesc_sk}')

    def test_compare_escape_schemes(self):
        r = test_escapables.collect_entries_for_escapes(test_escapables.entries, wordnet_xml.custom_char_escapes_for_sk)
        for k in r:
            v = r[k]
            if v:
                print(f'{k}')
                for i, e in enumerate(r[k]):
                    for s in e.senses:
                        sk, esc_sk, legacy_esc_sk = compare_xml_sensekeys(s.id)
                        if i < self.limit:
                            print(f'\t{sk}')
                            print(f'\t\t--now--> {esc_sk}')
                            print(f'\t\t--old--> {legacy_esc_sk}')
