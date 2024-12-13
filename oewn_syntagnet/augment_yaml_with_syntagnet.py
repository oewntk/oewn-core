#!/usr/bin/python3

"""
Augment YAML with SyntagNet collocations
Merges exported OEWN-SyntagNet into OEWN YAML files

Author: Bernard Bou <1313ou@gmail.com> for rewrite and revamp
"""

#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import argparse
import os
import sys
from glob import glob
from typing import Dict, Any, List

import yaml


def augment_yaml_files(out_dir, incoming: Dict[str, Any], files: List[str]):
    for file in files:
        name = os.path.basename(file)
        print(f'{name}', file=sys.stderr)
        with open(file) as f:
            base = yaml.safe_load(f)
            _deep_augment(base, incoming, 0)

            with open(f'{out_dir}/{name}', 'w') as out:
                yaml.dump(base, out, allow_unicode=True)


def _deep_augment(base: Dict, incoming: Dict, level: int) -> Dict:
    for key, value in base.items():
        if key in incoming:
            value2 = incoming[key]
            if isinstance(value, dict) and isinstance(value2, dict):
                _deep_augment(value, value2, level + 1)
            elif isinstance(value, list) and isinstance(value2, list):
                dd = {d['id']: d for d in value2}
                for d in value:
                    i = d['id']
                    if i in dd:
                        d2 = dd[i]
                        d.update(d2)
                # print(f'{'  ' * level}{key} - {value}')
    return base


def main() -> None:
    arg_parser = argparse.ArgumentParser(description="load syntagnet from yaml, merge it into yaml files")
    arg_parser.add_argument('in_dir', type=str, help='from-dir for yaml/pickle')
    arg_parser.add_argument('out_dir', type=str, help='out-dir for result')
    arg_parser.add_argument('syntagnet', type=str, nargs='?', default='syntagnet.yaml', help='syntagnet data')
    args = arg_parser.parse_args()

    with open(args.syntagnet) as f:
        print(f'{os.path.basename(args.syntagnet)}', file=sys.stderr)
        incoming = yaml.safe_load(f)
        if isinstance(incoming, dict):
            merge_files = sorted(glob(f'{args.in_dir}/entries-*.yaml'))
            augment_yaml_files(f'{args.out_dir}', incoming, merge_files)
        else:
            print("Cannot augment with non dictionaries {}", file=sys.stderr)


if __name__ == '__main__':
    main()
