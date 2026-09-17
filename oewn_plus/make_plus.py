"""
Generate Open English Wordnet+ the version of Open English Wordnet extended
with additional words and synsets from Open English Namenet.

Author: Bernard Bou <1313ou@gmail.com>
"""

#  Copyright (c) 2026.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import argparse
import os
import sys
import time
from types import NoneType
from typing import List, Dict, Tuple

from oewn_core.wordnet import WordnetModel, Entry, Sense, Synset
from oewn_core.wordnet_fromyaml import load_entries, load_synsets
from oewn_core.wordnet_toyaml import save

lex_file_nums: Dict[str, int] = {
    "adj.all": 0,
    "adj.pert": 1,
    "adv.all": 2,
    "noun.Tops": 3,
    "noun.act": 4,
    "noun.animal": 5,
    "noun.artifact": 6,
    "noun.attribute": 7,
    "noun.body": 8,
    "noun.cognition": 9,
    "noun.communication": 10,
    "noun.event": 11,
    "noun.feeling": 12,
    "noun.food": 13,
    "noun.group": 14,
    "noun.location": 15,
    "noun.motive": 16,
    "noun.object": 17,
    "noun.person": 18,
    "noun.phenomenon": 19,
    "noun.plant": 20,
    "noun.possession": 21,
    "noun.process": 22,
    "noun.quantity": 23,
    "noun.relation": 24,
    "noun.shape": 25,
    "noun.state": 26,
    "noun.substance": 27,
    "noun.time": 28,
    "verb.body": 29,
    "verb.change": 30,
    "verb.cognition": 31,
    "verb.communication": 32,
    "verb.competition": 33,
    "verb.consumption": 34,
    "verb.contact": 35,
    "verb.creation": 36,
    "verb.emotion": 37,
    "verb.motion": 38,
    "verb.perception": 39,
    "verb.possession": 40,
    "verb.social": 41,
    "verb.stative": 42,
    "verb.weather": 43,
    "adj.ppl": 44}


def analyze_intersect(wn: WordnetModel,
                      entries: List[Entry],  #
                      synsets: List[Synset],  #
                      ) -> NoneType:
    intersection = set(wn.entries).intersection(set(entries))
    print(f"intersection entries: {len(intersection)}", file=sys.stderr)

    intersection = set(wn.synsets).intersection(set(synsets))
    print(f"intersection synsets: {len(intersection)}", file=sys.stderr)


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
    print(f"synset relations: {count} {relations}", file=sys.stderr)

    # sense relations
    count = 0
    relations = set()
    for entry in entries:
        for s in entry.senses:
            for r in s.relations:
                # if count < 5: print(f"-SENSE RELATION: {r}")
                count += 1
                relations.add(r.relation_type)
    print(f"sense relations: {count} {relations}", file=sys.stderr)


def analyze(wn: WordnetModel,
            entries: List[Entry],  #
            #
            #
            synsets: List[Synset],  #
            #
            ) -> NoneType:
    analyze_intersect(wn, entries, synsets)
    analyze_relations(entries, synsets)


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


def make_sensekey(lemma: str, pos: str, lex_name: str, idx: int) -> str:
    def type_to_num(t: str) -> int:
        if t == 'n':
            return 1
        elif t == 'v':
            return 2
        elif t == 'a':
            return 3
        elif t == 'r':
            return 4
        elif t == 's':
            return 5
        else:
            raise Exception(t)

    def lex_name_to_num(n: str) -> int:
        return lex_file_nums[n]

    def pad2(n: int) -> str:
        return f"{n:02d}"

    lemma = lemma.replace(' ', '_').lower()
    return f"{lemma}%{type_to_num(pos)}:{pad2(lex_name_to_num(lex_name))}:{pad2(idx)}::99"


def handle_orphans(synsets: List[Synset],
                   entries: List[Entry],
                   member_resolver: Dict[Tuple[str, str], Entry],
                   entry_resolver: Dict[Tuple[str, str, str | NoneType], Entry]
                   ) -> NoneType:
    count = 0
    new_count = 0
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
                    new_count += 1
                member_resolver[(member, synset.id)] = entry
                entry_resolver[(member, pos, None)] = entry
                count += 1
    print(f"handled {count} member orphans member creating {new_count} entries")


def merge(wn: WordnetModel,
          entries: List[Entry],
          member_resolver: Dict[Tuple[str, str], Entry],  #
          synsets: List[Synset],
          ) -> WordnetModel:
    merge_entries(wn, entries)
    merge_synsets(wn, synsets)

    # handle_orphans([wn.synset_resolver['08506402-n']], wn.entries, wn.member_resolver | member_resolver, wn.entry_resolver)
    handle_orphans(wn.synsets, wn.entries, wn.member_resolver | member_resolver, wn.entry_resolver)

    # rebuild resolvers
    wn.synset_resolver = {synset.id: synset for synset in wn.synsets}
    wn.sense_resolver = {sense.id: sense for sense in wn.senses}
    wn.member_resolver = {(e.lemma, s): e for e in wn.entries for s in e.synsetids}

    print("merged")
    return wn


def run(wn: WordnetModel, oenn_dir: str, out_dir: str) -> WordnetModel:
    home = f"{oenn_dir}/data"
    if not os.path.exists(f"{home}/curated"):
        raise ValueError(f"Curated dir not found in {home}")

    path = f"{home}/curated"
    if os.path.exists(path):
        entries, sense_resolver, member_resolver = load_entries(path)
        synsets, synset_resolver = load_synsets(path)
        print(f"loaded {len(entries)} curated entries")
        print(f"loaded {len(synsets)} curated synsets")

        analyze(wn, entries, synsets)
        merge(wn, entries, member_resolver, synsets)

        # m = wn.member_resolver[('C-horizon', '08676407-n')]
        # e = wn.entry_resolver[('C-horizon', 'n', None)]
        # es1 = wn.entries_resolver_by_lemma['C-horizon']
        # es2 = wn.entries_resolver_by_lemma_pos[('C-horizon', 'n')]
        # print(m)
        # print(e)
        # print(es1)
        # print(es2)
        #
        # s = wn.synset_resolver['08511469-n']
        # print(s.members)
        # m = member_resolver.get(('Antarctic', '08511469-n'))
        # print(m)
        # m = member_resolver.get(('Antarctic Zone', '08511469-n'))
        # print(m)
        # m = member_resolver.get(('South Frigid Zone', '08511469-n'))
        # print(m)
        #
        # m = wn.member_resolver.get(('Antarctic', '08511469-n'))
        # print(m)
        # m = wn.member_resolver.get(('Antarctic Zone', '08511469-n'))
        # print(m)
        # m = wn.member_resolver.get(('South Frigid Zone', '08511469-n'))
        # print(m)

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
