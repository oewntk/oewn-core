#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite
from typing import Tuple

from oewn_xml.wordnet_xml import legacy_factory


def make_xml_sensekeys(sk) -> Tuple[str, str, str]:
    esc_sk = legacy_factory.escape_sensekey(sk)
    unesc_sk = legacy_factory.unescape_sensekey(esc_sk)
    if sk != unesc_sk:
        raise ValueError(f'unescaped != original: {sk} != {unesc_sk}')
    return sk, esc_sk, unesc_sk
