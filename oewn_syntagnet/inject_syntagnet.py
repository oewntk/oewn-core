#!/usr/bin/python3

"""
WordNet load SyntagNet YAML
Will have a normalizing effect, after which it's not modified

Author: Bernard Bou <1313ou@gmail.com> for rewrite and revamp
"""

#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import argparse
import sys
import time
from typing import Dict, Any, Set, Tuple
from xmlrpc.client import Boolean

import yaml

from oewn_core.wordnet import WordnetModel, Sense
from oewn_core.wordnet_fromyaml import load
from oewn_core.deserialize import load_pickle
from oewn_core.wordnet_toyaml import save


def make_sensekeys(wn: WordnetModel) -> Set[str]:
    sensekeys: Set = set()
    for s in wn.senses:
        sensekeys.add(s.id)
    return sensekeys


def inject_syntagnet_to_model(wn: WordnetModel, syntagnet: str, two_ways: Boolean = True) -> Tuple[int, int]:
    """
    WordNet inject SyntagNet as relations
    """
    count = 0
    with open(syntagnet, encoding='utf-8') as inp:
        fails = 0
        y: Dict[str, Any] = yaml.load(inp, Loader=yaml.CLoader)
        for sk1, collocations_y in y.items():
            # print(f'{sk} {collocations_y}')
            if sk1 in wn.sense_resolver:
                sense1 = wn.sense_resolver[sk1]
                # print(f'{sense1.id}')
                for sk2 in collocations_y["collocation"]:
                    if sk2 in wn.sense_resolver:
                        sense2 = wn.sense_resolver[sk2]
                        # print(f'\t{sense1.id}')

                        # type
                        t = Sense.Relation.Type.COLLOCATION
                        # t = Sense.Relation.Type.COLLOCATION if direction == TARGET else Sense.Relation.Type.COLLOCATION_INV

                        # add to sense 1
                        if sense1.relations is None:
                            sense1.relations = []
                        # print(f"add {sk1}-{t}->{sk2}")
                        sense1.relations.append(Sense.Relation(sk2, t))
                        count += 1

                        if two_ways:
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


def load_and_inject(in_dir: str, syntagnet: str, pickle: Boolean = False) -> WordnetModel:
    wn = load_pickle(in_dir) if pickle else load(in_dir)
    count, fails = inject_syntagnet_to_model(wn, syntagnet)
    print(f'{count} collocations {fails} fails', file=sys.stderr)
    return wn


def main() -> None:
    """
    WordNet load-save
    Will have a normalizing effect, after which it's not modified
    """
    arg_parser = argparse.ArgumentParser(description="load wn and SyntagNet from yaml, merge and save")
    arg_parser.add_argument('in_dir', type=str, help='from-dir')
    arg_parser.add_argument('out_dir', type=str, help='to-dir')
    arg_parser.add_argument('syntagnet', type=str, help='collocations')
    args = arg_parser.parse_args()
    pickle = True
    wn = load_and_inject(args.in_dir, args.syntagnet, pickle)
    save(wn, args.out_dir)


if __name__ == '__main__':
    start_time = time.time()
    main()
    end_time = time.time()
    duration = end_time - start_time
    print(f"Importing took {duration:.6f} seconds", file=sys.stderr)
