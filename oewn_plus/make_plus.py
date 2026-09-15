#  Copyright (c) 2026.
#  Creative Commons 4 for original code
#  GPL3 for rewrite
# Generate Open English Wordnet+ the version of Open English Wordnet extended
# with additional words and synsets from Open English Namenet.

import argparse
import os
import sys
import time
from types import NoneType
from typing import List, Dict, Tuple

from oewn_core.wordnet import WordnetModel, Entry, Sense, Synset
from oewn_core.wordnet_fromyaml import load_entries, load_synsets
from wordnet_toyaml import save


def pseudo_entries(self):
    for (lemma, pos), synsets in self._pseudo_entries:
        entry = Entry(lemma, pos, None)
        for idx, synset in enumerate(synsets):
            senseid = self.make_sensekey(lemma, pos, idx)
            synsetid = synset.id
            sense = Sense(senseid, entry, synsetid, adjposition=None)
            entry.senses.append(sense)
        yield entry


def recursively_sort(data):
    """Recursively sort the dictionary by keys."""
    if isinstance(data, dict):
        sorted_data = dict()
        for key in sorted(data.keys()):
            sorted_data[key] = recursively_sort(data[key])
        return sorted_data
    elif isinstance(data, list):
        return [recursively_sort(item) for item in data]
    else:
        return data


def make_sensekey(lemma, pos, lex_name, idx):
    lemma = lemma.replace(' ', '_')

    def to_num(type):
        if type == 'n':
            return 1
        elif type == 'v':
            return 2
        elif type == 'a':
            return 3
        elif type == 'r':
            return 4
        elif type == 's':
            return 5
        else:
            raise Exception(type)

    return f"{lemma}%{to_num(pos)}:{lex_name}:{idx + 1}"


def merge_entry(old_entry: Entry, new_entry: Entry):
    print(f"MERGE {old_entry} {new_entry}", file=sys.stderr)
    raise Exception(f"MERGE {old_entry} {new_entry}")


def merge_synset(old_synset: Synset, new_synset: Synset):
    print(f"MERGE {old_synset} {new_synset}", file=sys.stderr)
    raise Exception(f"MERGE {old_synset} {new_synset}")


def merge_entries(wn: WordnetModel,
                  entries: List[Entry],  #
                  ) -> WordnetModel:
    entry_resolver = wn.entry_resolver
    for entry in entries:
        resolved = entry.key in entry_resolver
        if resolved:
            print(f"OLD {entry}", file=sys.stderr)
        else:
            # print(f"NEW {entry}", file=sys.stderr)
            wn.entries.append(entry)
            entry_resolver[entry.key] = entry
    return wn


def merge_synsets(wn: WordnetModel,
                  synsets: List[Synset],  #
                  ) -> WordnetModel:
    synset_resolver = wn.synset_resolver
    for synset in synsets:
        resolved = synset.id in synset_resolver
        if resolved:
            old_synset = wn.synset_resolver[synset.id]
            merge_synset(old_synset, synset)
        else:
            # print(f"ADD {synset}", file=sys.stderr)
            wn.synsets.append(synset)
            synset_resolver[synset.id] = synset
    return wn


def build_member_resolver0(wn) -> Dict[Tuple[str, str], Entry]:
    def find_first(entries2: List[Entry], synsetid: str) -> Entry | None:
        try:
            return next(e for e in entries2 if synsetid in e.synsetids)
        except StopIteration:
            print(f"NOT FOUND {synsetid} {entries2} {[e.synsetids for e in entries2]}")

    entries_resolver = wn.entries_resolver_by_lemma_pos
    return {
        (lemma, synsetid): match
        for (lemma, pos, synsetid) in wn.synset_members
        if (match := find_first(entries_resolver.get((lemma, pos), []), synsetid)) is not None
    }


def build_member_resolver(wn) -> Dict[Tuple[str, str], Entry]:
    r = dict()
    for e in wn.entries:
        for s in e.synsetids:
            r[(e.lemma, s)] = e
    return r


def merge(wn: WordnetModel,
          entries: List[Entry],  #
          sense_resolver: Dict[str, Sense],  #
          member_resolver: Dict[Tuple[str, str], Entry],  #
          synsets: List[Synset],  #
          synset_resolver: Dict[str, Synset],  #
          ) -> WordnetModel:
    merge_entries(wn, entries)
    merge_synsets(wn, synsets)

    #handle_orphans([wn.synset_resolver['08506402-n']], wn.entries, wn.member_resolver | member_resolver, wn.entry_resolver)
    handle_orphans(wn.synsets, wn.entries, wn.member_resolver | member_resolver, wn.entry_resolver)

    # rebuild resolvers
    # wn.synset_resolver |= synset_resolver
    # wn.sense_resolver |= sense_resolver
    # wn.member_resolver |= member_resolver

    wn.synset_resolver = {synset.id: synset for synset in wn.synsets}
    wn.sense_resolver = {sense.id: sense for sense in wn.senses}
    wn.member_resolver = build_member_resolver(wn)

    s = sorted(wn.entries, key=lambda e: e.mkey)
    dupes = {x for i, x in enumerate(s) if i and x == s[i - 1]}
    print("DUPES ", dupes)

    print("MERGED")
    return wn


def analyze_duplicates(wn: WordnetModel,
                       entries: List[Entry],  #
                       synsets: List[Synset],  #
                       ) -> NoneType:
    # synsets
    count = 0
    for synset in synsets:
        if synset.id in wn.synset_resolver:
            if count < 5: print(f"-DUPLICATED: {synset.id}")
            count += 1
    print(f"DUPLICATED SYNSETS: {count}")

    # entries
    count = 0
    for entry in entries:
        if entry.mkey in wn.member_resolver:
            if count < 5: print(f"-DUPLICATED: {entry.mkey}")
            count += 1
    print(f"DUPLICATED ENTRIES BY NVAR: {count}")


def analyze_duplicates2(wn: WordnetModel,
                        entries: List[Entry],  #
                        synsets: List[Synset],  #
                        ) -> NoneType:
    # synsets
    intersection = set(wn.entries).intersection(set(entries))
    print(f"INTERSECTION ENTRIES BY NVAR: {len(intersection)}")

    # entries
    intersection = set(wn.synsets).intersection(set(synsets))
    print(f"INTERSECTION SYNSETS: {len(intersection)}")


def analyze_relations(entries: List[Entry],  #
                      synsets: List[Synset],  #
                      ) -> NoneType:
    # synset relations
    count = 0
    relations = set()
    for synset in synsets:
        for relation in synset.relations:
            # if count < 5: print(f"-SYNSET RELATION: {relation}")
            count += 1
            relations.add(relation.relation_type)
    print(f"SYNSET RELATIONS: {count} {relations}")

    # sense relations
    count = 0
    relations = set()
    for entry in entries:
        for s in entry.senses:
            for r in s.relations:
                # if count < 5: print(f"-SENSE RELATION: {r}")
                count += 1
                relations.add(r.relation_type)
    print(f"SENSE RELATIONS: {count} {relations}")


def handle_orphans(synsets: List[Synset],
                   entries: List[Entry],
                   member_resolver: Dict[Tuple[str, str], Entry],
                   entry_resolver: Dict[Tuple[str, str, str | NoneType], Entry]
                   ) -> NoneType:
    for synset in synsets:
        for member in synset.members:
            if (member, synset.id) not in member_resolver:
                pos = synset.nvar
                key = (member, pos, None)
                existing = entry_resolver.get(key)
                entry = existing if existing is not None else Entry(member, pos, None)
                sense_idx = 0 if entry.senses is None else len(entry.senses)
                sk = make_sensekey(member, pos, synset.lex_name, sense_idx)
                sense = Sense(sk, entry, synset.id)
                entry.senses.append(sense)
                if existing is None:
                    entries.append(entry)

                member_resolver[(member, synset.id)] = entry
                entry_resolver[(member, pos, None)] = entry


def get_orphans0(synsets: List[Synset],
                 member_resolver: Dict[Tuple[str, str], Entry]
                 ) -> List[Entry]:
    # orphan members
    orphan_members_by_key = dict()
    for synset in synsets:
        for member in synset.members:
            if (member, synset.id) not in member_resolver:
                pos = synset.nvar
                key = (member, pos, None)
                entry = orphan_members_by_key.get(key)
                if entry is None:
                    entry = Entry(member, pos, None)
                    orphan_members_by_key[key] = entry

                sense_idx = 0 if entry.senses is None else len(entry.senses)
                sense = Sense(make_sensekey(member, pos, synset.lex_name, sense_idx), entry, synset.id)
                entry.senses.append(sense)
    orphan_members = (orphan_members_by_key.values())
    return sorted(orphan_members, key=lambda e: e.mkey)


def analyze(wn: WordnetModel,
            entries: List[Entry],  #
            sense_resolver: Dict[str, Sense],  #
            member_resolver: Dict[Tuple[str, str], Entry],  #
            synsets: List[Synset],  #
            synset_resolver: Dict[str, Synset],  #
            ) -> NoneType:
    analyze_duplicates(wn, entries, synsets)
    analyze_duplicates2(wn, entries, synsets)
    analyze_relations(entries, synsets)


def run(wn: WordnetModel, oenn_dir: str, out_dir: str) -> WordnetModel:
    home = f"{oenn_dir}/data"
    if not os.path.exists(f"{home}/addendum/sense_orders.yaml"):
        raise ValueError(f"Addendum file not found: {home}/addendum/sense_orders.yaml")

    path = f"{home}/curated"
    if os.path.exists(path):
        entries, sense_resolver, member_resolver = load_entries(path)
        synsets, synset_resolver = load_synsets(path)
        print(f"Loaded {len(entries)} curated entries", file=sys.stderr)
        print(f"Loaded {len(synsets)} curated synsets", file=sys.stderr)

        analyze(wn, entries, sense_resolver, member_resolver, synsets, synset_resolver)
        merge(wn, entries, sense_resolver, member_resolver, synsets, synset_resolver)

        #m = wn.member_resolver[('C-horizon', '08676407-n')]
        #e = wn.entry_resolver[('C-horizon', 'n', None)]
        #es1 = wn.entries_resolver_by_lemma['C-horizon']
        #es2 = wn.entries_resolver_by_lemma_pos[('C-horizon', 'n')]
        #print(m)
        #print(e)
        #print(es1)
        #print(es2)
#
        #s = wn.synset_resolver['08511469-n']
        #print(s.members)
        #m = member_resolver.get(('Antarctic', '08511469-n'))
        #print(m)
        #m = member_resolver.get(('Antarctic Zone', '08511469-n'))
        #print(m)
        #m = member_resolver.get(('South Frigid Zone', '08511469-n'))
        #print(m)
#
        #m = wn.member_resolver.get(('Antarctic', '08511469-n'))
        #print(m)
        #m = wn.member_resolver.get(('Antarctic Zone', '08511469-n'))
        #print(m)
        #m = wn.member_resolver.get(('South Frigid Zone', '08511469-n'))
        #print(m)

        save(wn, out_dir)
    return wn


def main() -> WordnetModel:
    arg_parser = argparse.ArgumentParser(description="load yaml from namenet")
    arg_parser.add_argument('in_dir', type=str, help='from-dir')
    arg_parser.add_argument("oenn_dir", type=str, help="Directory containing Open English Namenet files")
    arg_parser.add_argument('--pickle', action='store_true', default=False, help='use pickle')
    arg_parser.add_argument('--pickled', type=str, default='oewn.pickle', help='from-pickle')
    arg_parser.add_argument('out_dir', type=str, help='to-dir')
    args = arg_parser.parse_args()

    def get_wn() -> WordnetModel:
        if args.pickle:
            from oewn_core.deserialize import load as pickle_load
            return pickle_load(args.in_dir, args.pickled)  # , extend=True
        from oewn_core.wordnet_fromyaml import load as yaml_load
        return yaml_load(args.in_dir)  # , extend=True

    _wn: WordnetModel = get_wn()
    print(f"Info {_wn.info()}")
    _xwn = run(_wn, args.oenn_dir, args.out_dir)
    print(f"Info {_xwn.info()}")
    return _xwn


if __name__ == '__main__':
    start_time = time.time()
    main()
    end_time = time.time()
    duration = end_time - start_time
    print(f"Loading and processing took {duration:.6f} seconds", file=sys.stderr)
