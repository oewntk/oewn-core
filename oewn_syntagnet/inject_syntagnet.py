#!/usr/bin/python3

"""
Inject SyntagNet (YAML) into the model

Author: Bernard Bou <1313ou@gmail.com> for rewrite and revamp
"""

#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import argparse
import sys
import time
from typing import Dict, Any, Set, Tuple, Optional

import yaml

from oewn_core.wordnet import WordnetModel, Sense


def make_sensekeys(wn: WordnetModel) -> Set[str]:
    """
    :param wn: model
    :return: set of sensekeys in the model
    """
    sensekeys: Set = set()
    for s in wn.senses:
        sensekeys.add(s.id)
    return sensekeys


def inject_syntagnet_to_model(wn: WordnetModel, syntagnet: str, two_ways: bool = True) -> Tuple[int, int]:
    """
    WordNet inject SyntagNet as relations
    :param wn: model
    :param syntagnet: path to SyntagNet YAML data
    :param two_ways: whether to add inverse relations also
    :return: count of additions and failures
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
                print(f'{sk1} source not resolvable in collocation for {sk1}', file=sys.stderr)
                fails += 1
            sense1.relations = list(sorted(set(sense1.relations), key=lambda r: (r.relation_type, r.target)))
            if two_ways:
                sense2.relations = list(sorted(set(sense2.relations), key=lambda r: (r.relation_type, r.target)))

    return count, fails


def load_and_inject(in_dir: str, syntagnet: str, pickled: Optional[str] = None) -> WordnetModel:
    """
    Load Wordnet and SyntagNet from YAML, inject sn into wn
    :param in_dir: home dir for YAML or pickled model file(s)
    :param syntagnet: path to SyntagNet YAML data
    :param pickled: whether to use pickled model
    :return: Syntagnet-augmented model
    """

    def get_model() -> WordnetModel:
        if pickled:
            from oewn_core.deserialize import load
            return load(in_dir, file=pickled)
        else:
            from oewn_core.wordnet_fromyaml import load
            return load(in_dir, resolve=True)

    wn = get_model()
    count, fails = inject_syntagnet_to_model(wn, syntagnet)
    print(f'{count} collocations {fails} fails', file=sys.stderr)
    return wn


def main() -> None:
    """
    WordNet + SyntagNet load-save
    :command-line: oewn_home output_home syntagnet_file
    """
    from oewn_core.wordnet_toyaml import save
    arg_parser = argparse.ArgumentParser(description="load wn and SyntagNet from yaml, inject and save")
    arg_parser.add_argument('--pickle', action='store_true', default=False, help='use pickle')
    arg_parser.add_argument('in_dir', type=str, help='from-dir')
    arg_parser.add_argument('out_dir', type=str, help='to-dir')
    arg_parser.add_argument('syntagnet', type=str, help='collocations')
    arg_parser.add_argument('pickled', type=str, nargs='?', default=None, help='from-pickle')
    args = arg_parser.parse_args()
    wn = load_and_inject(args.in_dir, args.syntagnet, args.pickled if args.pickle else None)
    save(wn, args.out_dir)


if __name__ == '__main__':
    start_time = time.time()
    main()
    end_time = time.time()
    duration = end_time - start_time
    print(f"Injecting took {duration:.6f} seconds", file=sys.stderr)
