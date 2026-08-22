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
from typing import List, Dict, Tuple

import yaml

from oewn_core.wordnet import WordnetModel, Entry, Sense, Synset, PartOfSpeech, Example, Pronunciation, VerbFrame
from oewn_core.wordnet_fromyaml import load_entries, load_synsets


def entry_id_by_lemma_synset_id(self, lemma, synset_id, prefix):
    for e in self.entry_by_lemma(lemma):
        for s in self.entry_by_id(e).senses:
            if s.synset == synset_id:
                return e
    self._pseudo_entries[(lemma, synset_id[-1])].append(synset_id)
    return None


def pseudo_entries(self):
    for (lemma, pos), synsets in self._pseudo_entries:
        entry = Entry(lemma, pos, None)
        for idx, synset in enumerate(synsets):
            senseid = self.make_sensekey(lemma, pos, idx)
            synsetid = synset.id
            sense = Sense(senseid, entry, synsetid, adjposition=None)
            entry.senses.append(sense)
        yield entry


def compare_pronunciations(pron1, pron2):
    """Compare two pronunciation entries for equality."""
    if pron1.keys() != pron2.keys():
        return False
    for key in pron1:
        if pron1[key] != pron2[key]:
            return False
    return True


def merge_addendum(path):
    for f in glob(f'{path}/entries-*.yaml'):
        filename = f.split("/")[-1]
        print(f"  Merging addendum for {filename}...")
        with open(f"{path}/{filename}") as x_file:
            y = yaml.safe_load(x_file)
            # merge_addendum(wn, add_data, sense_orders)
    noun_files = glob(f'{path}/noun*.yaml')
    verb_files = glob(f'{path}/verb*.yaml')
    adj_files = glob(f'{path}/adj*.yaml')
    adv_files = glob(f'{path}/adv*.yaml')
    for f in noun_files + verb_files + adj_files + adv_files:
        filename = f.split("/")[-1]
        print(f"  Merging curated for {filename}...")
        with open(f"{path}/{filename}") as x_file:
            y = yaml.safe_load(x_file)
            # merge_addendum_both(wn, y, sense_orders)


def merge_addendum_both(data, add, sense_orders):
    """Merge the addendum data together. Recursively merge the dictionaries,
    together, raising an exception if there are any key conflicts.
    A special case is `sense` where we must match the `id` field when
    merging"""
    for key, value in add.items():
        if key not in data:
            data[key] = value
        else:
            if isinstance(value, dict):
                merge_addendum(data[key], value, sense_orders.get(key, {}))
            elif isinstance(value, list):
                if key == "sense":
                    id2sense = {sense["id"]: sense for sense in data[key]}
                    for sense in value:
                        if sense["id"] in id2sense:
                            merge_addendum(id2sense[sense["id"]], sense, {})
                        else:
                            data[key].append(sense)

                    # If sense_orders is a list, then sort the senses by this list
                    if isinstance(sense_orders, list):
                        id_order = {sid: i for i, sid in enumerate(sense_orders)}
                        data[key].sort(key=lambda s: id_order.get(s["id"], len(id_order)))
                elif key == "pronunciation":
                    for pron in value:
                        if not any(compare_pronunciations(pron, existing) for existing in data[key]):
                            data[key].append(pron)
                else:
                    data[key].extend(value)
            elif isinstance(value, str) and isinstance(data[key], str) and data[key] == value:
                pass
            else:
                print(type(value))
                raise ValueError(f"Conflict at key {key}: {data[key]} vs {value}")


def merge_curated_entries(wn: WordnetModel, y):
    """Merge the curated data together. For entries, we match the first two keys (lemma and pos) when merging."""
    for lemma, by_pos in y.items():
        if lemma not in wn:
            wn.lexes.add[lemma] = by_pos
        else:
            for pos, entry in by_pos.items():
                if pos not in wn[lemma]:
                    wn[lemma][pos] = entry
                else:
                    merge_addendum(wn[lemma][pos], entry, {})


def merge_curated_synsets(wn: WordnetModel, curated):
    """Merge the curated data together. For other files, we merge by key."""
    # Check the keys are disjoint
    for key in curated:
        if key in wn:
            raise ValueError(f"Conflict at key {key} during curated merge")
    wn.update(curated)


def merge_curated(wn: WordnetModel, path: str):
    for f in glob(f"{path}/*.yaml"):
        filename = f.split("/")[-1]
        print(f"  Merging curated for {filename}...")
        with open(f"{path}/{filename}") as x_file:
            data = yaml.safe_load(x_file)
            merge_curated_entries(wn, data)
    noun_files = glob(f'{path}/noun*.yaml')
    verb_files = glob(f'{path}/verb*.yaml')
    adj_files = glob(f'{path}/adj*.yaml')
    adv_files = glob(f'{path}/adv*.yaml')
    for f in noun_files + verb_files + adj_files + adv_files:
        filename = f.split("/")[-1]
        print(f"  Merging curated for {filename}...")
        with open(f"{path}/{filename}") as x_file:
            y = yaml.safe_load(x_file)
            merge_curated_synsets(wn, y)


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


def make_sensekey(lemma, pos, idx):
    lemma = lemma.replace(' ','_')
    return f"{lemma}%pseudo:{pos}:{idx + 1}"


def merge_entry(old_entry: Entry, new_entry: Entry):
    print(f"MERGE {old_entry} {new_entry}", file=sys.stderr)
    pass


def merge_synset(old_synset: Synset, new_synset: Synset):
    print(f"MERGE {old_synset} {new_synset}", file=sys.stderr)
    pass


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
            wn.synset_resolver[synset.id] = synset
    return wn


def merge(wn: WordnetModel,
          entries: List[Entry],  #
          sense_resolver: Dict[str, Sense],  #
          member_resolver: Dict[Tuple[str, str], Entry],  #
          synsets: List[Synset],  #
          synset_resolver: Dict[str, Synset],  #
          ) -> WordnetModel:
    merge_entries(wn, entries)
    merge_synsets(wn, synsets)

    # pseudos
    entries_resolver = wn.entries_resolver_by_lemma_pos
    pseudos = []
    for synset in wn.synsets:
        for member in synset.members:
            pos = synset.nvar
            if (member, pos) not in entries_resolver:
                e = Entry(member, pos, None)
                s = Sense(make_sensekey(member, pos, len(e.senses)), e, synset.id)
                e.senses.append(s)
                pseudos.append(e)
    print(f"PSEUDOS: {len(pseudos)}")
    for e in sorted(pseudos, key=lambda e: e.key):
        print(f"-PSEUDO {e} {e.sensekeys}")
        wn.entries.append(e)

    r = wn.entries_resolver_by_lemma
    for e in r["Antarctic"]:
        print(f"{e} {e.sensekeys} {e.synsetids}")
    for e in r["zany"]:
        print(f"{e} {e.sensekeys} {e.synsetids}")

    #           wn.entries.append(e)
    #           entries_resolver[(member, pos)] = [e]

    # for synset in wn.synsets:
    #    for member in synset.members:
    #        pos = synset.nvar
    #        if (member, pos) not in entries_resolver:
    #            print("AGAIN", (member, pos), entries_resolver_by_lemma[member])

    # rebuild resolvers
    # def find_first(entries: List[Entry], synsetid: str) -> Entry:
    #    try:
    #        return next(e for e in entries if synsetid in e.synsetids)
    #    except StopIteration:
    #        print(f"NOT FOUND {synsetid} {entries} {[e.synsetids for e in entries]}")
    #
    # wn.sense_resolver = {sense.id: sense for sense in wn.senses}
    # wn.member_resolver = {(lemma, synsetid): find_first(entries_resolver[(lemma, pos)], synsetid) for (lemma, pos, synsetid) in wn.synset_members}

    return wn


def run(wn: WordnetModel, oenn_dir: str) -> WordnetModel:
    home = f"{oenn_dir}/data"
    if not os.path.exists(f"{home}/addendum/sense_orders.yaml"):
        raise ValueError(f"Addendum file not found: {home}/addendum/sense_orders.yaml")

    with open(f"{home}/addendum/sense_orders.yaml") as so_file:
        sense_orders = yaml.safe_load(so_file)

        # path = f"{home}/addendum"
        # if os.path.exists(path):
        #     entries, sense_resolver, member_resolver = load_entries(path)
        #     synsets, synset_resolver = load_synsets(path)
        #     print(f"Loaded {len(entries)} curated entries", file=sys.stderr)
        #     print(f"Loaded {len(synsets)} curated synsets", file=sys.stderr)
        #     merge(wn, entries, sense_resolver, member_resolver, synsets, synset_resolver)

        path = f"{home}/curated"
        if os.path.exists(path):
            entries, sense_resolver, member_resolver = load_entries(path)
            synsets, synset_resolver = load_synsets(path)
            print(f"Loaded {len(entries)} curated entries", file=sys.stderr)
            print(f"Loaded {len(synsets)} curated synsets", file=sys.stderr)
            merge(wn, entries, sense_resolver, member_resolver, synsets, synset_resolver)

        # wn = recursively_sort(wn)

        # with open("src/plus/" + filename, "w") as out_file:
        #    yaml.dump(data, out_file, sort_keys=False, allow_unicode=True)

    return wn


def main() -> WordnetModel:
    arg_parser = argparse.ArgumentParser(description="load from namenet from yaml")
    arg_parser.add_argument('in_dir', type=str, help='from-dir')
    arg_parser.add_argument("oenn_dir", type=str, help="Directory containing Open English Namenet files")
    arg_parser.add_argument('--pickle', action='store_true', default=False, help='use pickle')
    arg_parser.add_argument('--pickled', type=str, default='oewn.pickle', help='from-pickle')
    # arg_parser.add_argument('out_dir', type=str, help='to-dir')
    args = arg_parser.parse_args()

    def get_wn() -> WordnetModel:
        if args.pickle:
            from oewn_core.deserialize import load as pickle_load
            return pickle_load(args.in_dir, args.pickled)  # , extend=True
        from oewn_core.wordnet_fromyaml import load as yaml_load
        return yaml_load(args.in_dir)  # , extend=True

    _wn: WordnetModel = get_wn()
    print(f"Info {_wn.info()}")
    _xwn = run(_wn, args.oenn_dir)
    print(f"Info {_xwn.info()}")
    return _xwn


if __name__ == '__main__':
    start_time = time.time()
    main()
    end_time = time.time()
    duration = end_time - start_time
    print(f"Loading and processing took {duration:.6f} seconds", file=sys.stderr)
