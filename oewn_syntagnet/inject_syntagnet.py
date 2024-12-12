#!/usr/bin/python3

"""
WordNet load SyntagNet YAML
Will have a normalizing effect, after which it's not modified

Author: Bernard Bou <1313ou@gmail.com> for rewrite and revamp
"""
#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import sys
from typing import Dict, Any, Set, Tuple
from xmlrpc.client import Boolean

import yaml

from wordnet import WordnetModel, Sense


def make_sensekeys(wn: WordnetModel) -> Set[str]:
    sensekeys: Set = set()
    for s in wn.senses:
        sensekeys.add(s.id)
    return sensekeys


def add_syntagnet_to_model(wn: WordnetModel, syntagnet: str, twoways: Boolean) -> Tuple[int,int]:
    """
    WordNet inject SyntagNet as relations
    """
    count = 0
    with open(syntagnet, encoding='utf-8') as inp:
        fails = 0
        y: Dict[str, Any] = yaml.load(inp, Loader=yaml.CLoader)
        for sk1, collocations_y in y.items():
            # print(f'{sk} {collocations_y}')
            sense1 = wn.sense_resolver[sk1]
            if sense1:
                print(f'{sense1.id}')
                for sk2 in collocations_y["collocation"]:
                    sense2 = wn.sense_resolver[sk2]
                    if sense2:
                        print(f'\t{sense1.id}')

                        # type
                        t = Sense.Relation.Type.COLLOCATION
                        # t = Sense.Relation.Type.COLLOCATION if direction == TARGET else Sense.Relation.Type.COLLOCATION_INV

                        # add to sense 1
                        if sense1.relations is None:
                            sense1.relations = []
                        # print(f"add {sk1}-{t}->{sk2}")
                        sense1.relations.append(Sense.Relation(sk2, t))
                        count += 1

                        # add to sense 2
                        if sense2.relations is None:
                            sense2.relations = []
                        # print(f"add {sk2}-{t}->{sk1}")
                        sense2.relations.append(Sense.Relation(sk1, t))
                        count += 1

                else:
                    print(f'{sk2} target not resolvable in collocation {sk1}-{sk2}', file=sys.stderr)
                    fails += 1

            else:
                print(f'{sk2} source not resolvable in collocation {sk1}-{sk2}', file=sys.stderr)
                fails += 1
    return count, fails
