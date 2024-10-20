#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite
import os
import sys

import deserialize

data_home = os.environ['OEWN_HOME']
print(f'data={data_home}', file=sys.stderr)
wn = deserialize.load_pickle(data_home)
entries = sorted(list(wn.entries), key=lambda e: e.lemma)
senses = wn.senses

def collect_entries_for_escapes(entries, escape_map):
    r = {}
    for k in escape_map:
        if k == ' ':
            continue
        r[k] = []
        for e in entries:
            if k in e.lemma:
                r[k].append(e)
    return r


def print_as_dictionary(r, limit=5):
    print('escapable = {')
    for k, v in r.items():
        print(f'\t"{k}": (')
        i = 0
        for e in v:
            if i > limit:
                print(f'\t\t# ... {len(r[k])} total')
                break
            print(f'\t\t{e.key},')
            i += 1
        print('\t),')
    print('}')
