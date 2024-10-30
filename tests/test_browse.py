#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite
import argparse

from wordnet import WordnetModel


def browse(wn: WordnetModel) -> None:
    entity_resolver = wn.entry_resolver
    e = entity_resolver[('force', 'n', None)]
    print(f'{e}')
    for s in e.senses:
        ss = s.resolved_synset
        print(f'\t{s} -> {ss.members} {ss.definitions}')
        for ssr in ss.relations:
            print(f'\t\t{ssr} {ssr.resolved_target.members} {ssr.resolved_target.definitions}')
        for sr in s.relations:
            print(f'\t\t{sr} {sr.resolved_target}')


def main() -> None:
    def get_model() -> WordnetModel:
        if args.pickle:
            from oewn_core.deserialize import load
            return load(args.in_dir, resolve=True)
        else:
            from oewn_core.wordnet_fromyaml import load
            return load(args.in_dir, resolve=True)

    arg_parser = argparse.ArgumentParser(description="browse")
    arg_parser.add_argument('--serialized', action='store_true', default='True', help='model to use')
    arg_parser.add_argument('in_dir', type=str, help='from-dir for pickle')
    arg_parser.add_argument('pickle', type=str, nargs='?', default='oewn.pickle', help='from-pickle')
    args = arg_parser.parse_args()

    wn = get_model()
    browse(wn)


if __name__ == '__main__':
    main()
