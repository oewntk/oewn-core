#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite
from typing import Tuple

from oewn_xml.wordnet_xml import legacy_factory, to_xml_sense_id, from_xml_sense_id


def process_sensekey(sk) -> Tuple[str, str, str]:
    senseid = to_xml_sense_id(sk, legacy_factory)
    sk2 = from_xml_sense_id(senseid, legacy_factory)
    if sk != sk2:
        raise ValueError(f'unescaped != original: {sk} != {senseid}')
    return sk, senseid, sk2
