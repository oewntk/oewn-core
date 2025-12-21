#!/usr/bin/python3

"""
WordNet load-tweak-save
Will have a normalizing effect, after which it's not modified

Author: Bernard Bou <1313ou@gmail.com> for rewrite and revamp
"""

#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import argparse
import sys
import time
from collections.abc import Callable
from typing import Dict, Tuple

from oewn_core.yaml_to_yaml import main

from oewn_core.wordnet import Entry, Synset, WordnetModel


def strip_orphaned_member(synset: Synset, member_resolver: Dict[Tuple[str, str], Entry]):
    for m in synset.members[:]:  # shallow copy
        if (m, synset.id) not in member_resolver:
            synset.members.remove(m)
            print(f"removed member {m} in {synset.id}", file=sys.stderr)


def strip_orphaned_members(wn: WordnetModel):
    for s in wn.synsets:
        strip_orphaned_member(s, wn.member_resolver)
    return wn


def _default_processing(wn: WordnetModel) -> WordnetModel:
    pass


def get_processing(name: str) -> Callable[[WordnetModel], WordnetModel]:
    return globals()[name] if name else None


if __name__ == '__main__':
    start_time = time.time()
    arg_parser = argparse.ArgumentParser(description="load from yaml, process and save")
    arg_parser.add_argument('in_dir', type=str, help='from-dir')
    arg_parser.add_argument('out_dir', type=str, help='to-dir')
    arg_parser.add_argument('processf', type=str, help='process')
    args = arg_parser.parse_args()

    processf_name = args.processf
    processf = get_processing(processf_name) if processf_name else None
    if processf:
        print(f"processing {processf}")

    main(args.in_dir, args.out_dir, processf)
    end_time = time.time()
    duration = end_time - start_time
    print(f"Processing took {duration:.6f} seconds", file=sys.stderr)
