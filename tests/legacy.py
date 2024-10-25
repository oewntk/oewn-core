#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

from xml.wordnet_xml import legacy_factory


def make_xml_sensekeys(sk):
    esc_sk = legacy_factory.escape_sensekey(sk)
    unesc_sk = legacy_factory.unescape_sensekey(esc_sk)
    if sk != unesc_sk:
        raise ValueError(f'unescaped != original: {sk} != {unesc_sk}')
    return sk, esc_sk, unesc_sk
