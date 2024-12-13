"""
WordNet model browse sample
Author: John McCrae <john@mccr.ae> for original code
Author: Bernard Bou <1313ou@gmail.com> for rewrite and revamp
"""
#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import argparse

from oewn_core.wordnet import WordnetModel


def browse(wn: WordnetModel) -> None:
    entity_resolver = wn.entry_resolver
    e = entity_resolver[('force', 'n', None)]
    print(f'{e}')
    for s in e.senses:
        ss = s.resolved_synset
        assert ss is not None
        print(f'\t{s} -> {ss.members} {ss.definitions}')
        for ssr in ss.relations:
            assert ssr.resolved_target
            print(f'\t\t{ssr} {ssr.resolved_target.members} {ssr.resolved_target.definitions}')
        for sr in s.relations:
            assert sr.resolved_target
            print(f'\t\t{sr} {sr.resolved_target}')


def main() -> None:
    def get_model() -> WordnetModel:
        if args.pickle:
            from oewn_core.deserialize import load
            return load(args.in_dir, file=args.pickled, resolve=True)
        else:
            from oewn_core.wordnet_fromyaml import load
            return load(args.in_dir, resolve=True)

    arg_parser = argparse.ArgumentParser(description="browse")
    arg_parser.add_argument('--pickle', action='store_true', default=False, help='use pickle')
    arg_parser.add_argument('in_dir', type=str, help='from-dir for yaml/pickle')
    arg_parser.add_argument('pickled', type=str, nargs='?', default='oewn.pickle', help='from-pickle')
    args = arg_parser.parse_args()

    wn = get_model()
    browse(wn)


if __name__ == '__main__':
    main()
