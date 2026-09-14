#  Copyright (c) 2026.
#  Creative Commons 4 for original code
#  GPL3 for rewrite
# Generate Open English Wordnet+ the version of Open English Wordnet extended
# with additional words and synsets from Open English Namenet.

import sys
import time
from glob import glob
import argparse
import os
from types import NoneType
from typing import List, Dict, Tuple

import yaml

from oewn_core.wordnet import WordnetModel, Entry, Sense, Synset, PartOfSpeech, Example, Pronunciation, VerbFrame
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


def merge(wn: WordnetModel,
          entries: List[Entry],  #
          sense_resolver: Dict[str, Sense],  #
          member_resolver: Dict[Tuple[str, str], Entry],  #
          synsets: List[Synset],  #
          synset_resolver: Dict[str, Synset],  #
          ) -> WordnetModel:
    merge_entries(wn, entries, )
    merge_synsets(wn, synsets)

    wn.synset_resolver |= synset_resolver
    wn.sense_resolver |= sense_resolver
    wn.member_resolver |= member_resolver

    # rebuild resolvers
    #wn.synset_resolver = {synset.id: synset for synset in wn.synsets}
    #wn.sense_resolver = {sense.id: sense for sense in wn.senses}

    #def find_first(entries2: List[Entry], synsetid: str) -> Entry|None:
    #   try:
    #       return next(e for e in entries2 if synsetid in e.synsetids)
    #   except StopIteration:
    #       print(f"NOT FOUND {synsetid} {entries} {[e.synsetids for e in entries]}")
#
    #entries_resolver = wn.entries_resolver_by_lemma_pos
    #wn.member_resolver = {
    #    (lemma, synsetid): match
    #    for (lemma, pos, synsetid) in wn.synset_members
    #    if (match := find_first(entries_resolver.get((lemma, pos), []), synsetid)) is not None
    #}

    orphan_entries: List[Entry] = analyze_members(wn.synsets, wn.member_resolver)
    wn.entries += orphan_entries

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


def analyze_relations(entries: List[Entry],  #
                      synsets: List[Synset],  #
                      ) -> NoneType:
    # synset relations
    count = 0
    relations = set()
    for synset in synsets:
        for relation in synset.relations:
            #if count < 5: print(f"-SYNSET RELATION: {relation}")
            count += 1
            relations.add(relation.relation_type)
    print(f"SYNSET RELATIONS: {count} {relations}")

    # sense relations
    count = 0
    relations = set()
    for entry in entries:
        for s in entry.senses:
            for r in s.relations:
                #if count < 5: print(f"-SENSE RELATION: {r}")
                count += 1
                relations.add(r.relation_type)
    print(f"SENSE RELATIONS: {count} {relations}")


def analyze_members(synsets: List[Synset],
                    member_resolver: Dict[Tuple[str, str], Entry]
                    ) -> List[Entry]:
    # orphan members
    orphan_members = []
    for synset in synsets:
        for member in synset.members:
            if (member, synset.id) not in member_resolver:
                pos = synset.nvar
                entry = Entry(member, pos, None)
                sense = Sense(make_sensekey(member, pos, synset.lex_name, 0), entry, synset.id)
                entry.senses.append(sense)
                orphan_members.append(entry)
    count = 0
    print(f"ORPHAN MEMBERS: {len(orphan_members)}")
    for entry in sorted(orphan_members, key=lambda e: e.key):
        print(f"-ORPHAN MEMBER {entry} {entry.sensekeys} {entry.synsetids}")
        count += 1
    return orphan_members

def analyze(wn: WordnetModel,
            entries: List[Entry],  #
            sense_resolver: Dict[str, Sense],  #
            member_resolver: Dict[Tuple[str, str], Entry],  #
            synsets: List[Synset],  #
            synset_resolver: Dict[str, Synset],  #
            ) -> NoneType:
    analyze_duplicates(wn, entries, synsets)
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
