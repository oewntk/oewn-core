"""
WordNet model validation
This is validation of model's semantics
This validation does not validate XML form (use an XML validator)

Author: John McCrae <john@mccr.ae> for original code
Author: Bernard Bou <1313ou@gmail.com> for rewrite and revamp
"""
#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import argparse
import re
import sys
from collections import Counter
from typing import Dict, Pattern, Tuple

from oewn_core.wordnet import Entry, Synset, Sense, PartOfSpeech, WordnetModel


class ValidationError(Exception):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)


break_on_error = True


def warn(message: str) -> None:
    if break_on_error:
        raise ValidationError(message)
    else:
        print(message, file=sys.stderr)


# I D   V A L I D A T I O N

valid_id: Pattern = re.compile(fr"^.+$")

# valid_lemma = f'[^ %:]+'
valid_lemma: str = f'[^ %]+'

# valid_head = f'[^ %:]*'
valid_head: str = f'[^ %]*'

valid_sense_id: Pattern = re.compile(fr'^{valid_lemma}%([0-9]):[0-9]{{2}}:[0-9]{{2}}:{valid_head}:[0-9]{{0,2}}$')

valid_synset_id: Pattern = re.compile('^[0-9]{8}-([nvars])$')


def check_valid_id(any_id: str) -> None:
    if not bool(valid_id.match(any_id)):
        warn(f'{any_id} is not well-formed id')


def check_valid_synset_id(synset_id: str) -> None:
    check_valid_id(synset_id)
    if not bool(valid_synset_id.match(synset_id)):
        warn(f'{synset_id} is not well-formed synset id')


def check_valid_sense_id(sense_id: str) -> None:
    check_valid_id(sense_id)
    if not bool(valid_sense_id.match(sense_id)):
        warn(f'{sense_id} is not well-formed sense id')


def check_valid_sense_id_for_target(sense_id: str, target_id: str) -> None:
    m = valid_sense_id.match(sense_id)
    assert m is not None
    g = m.group(1)
    pos = ss_types_reverse[int(g)]
    m2 = valid_synset_id.match(target_id)
    assert m2 is not None
    g2 = m2.group(1)
    pos2 = PartOfSpeech(g2)
    if pos != pos2:
        warn(f'{target_id} target of {sense_id} is not well-formed')


# U T I L I T I E S   F O R   S E N S E K E Y S

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
    "adj.ppl": 44,
    "contrib.colloq": 50,
    "contrib.plwn": 51}

ss_types: Dict[PartOfSpeech, int] = {
    PartOfSpeech.NOUN: 1,
    PartOfSpeech.VERB: 2,
    PartOfSpeech.ADJECTIVE: 3,
    PartOfSpeech.ADVERB: 4,
    PartOfSpeech.ADJECTIVE_SATELLITE: 5
}
ss_types_reverse: Dict[int, PartOfSpeech] = {ss_types[k]: k for k in ss_types}

sense_id_lex_id: Pattern[str] = re.compile(".*%\\d:\\d\\d:(\\d\\d):.*")


def gen_lex_id(entry: Entry, sense: Sense) -> int:
    max_id = 0
    unseen = 1
    seen = False
    for s2 in entry.senses:
        if s2.id:
            m = re.match(sense_id_lex_id, s2.id)
            assert m is not None
            max_id = max(max_id, int(m.group(1)))
        else:
            if not seen:
                if s2.id == sense.id:
                    seen = True
                else:
                    unseen += 1
    return max_id + unseen


def extract_lex_id(sense_key: str) -> int:
    m = re.match(sense_id_lex_id, sense_key)
    assert m is not None
    return int(m.group(1))


def get_head_word(wn: WordnetModel, sense: Sense) -> Tuple[str, str] | None:
    synset = wn.synset_resolver[sense.synsetid]
    similars = [r for r in synset.relations if
                Synset.Relation.Type(r.relation_type) == Synset.Relation.Type.SIMILAR and
                # ignore satellites in non-Princeton sets
                not r.target.startswith("9") and
                not r.target.startswith("8")]
    if len(similars) == 1:
        target_id = similars[0].target
        target = wn.synset_resolver[target_id]
        target_entry = wn.member_resolver[(target.members[0], target.id)]
        target_sense = next((s for s in target_entry.senses if s.synsetid == target_id), None)
        assert target_sense is not None
        head = target_sense.id[:target_sense.id.rindex('%')]
        m = re.match(sense_id_lex_id, target_sense.id)
        assert m is not None
        head_id = m.group(1)
        return head, head_id
    warn(f'Could not deduce target of satellite {sense.id}')


def make_sense_key(wn: WordnetModel, entry: Entry, sense: Sense) -> str:
    """Calculate the sense key for a sense of an entry"""
    lemma = entry.lemma.lower().replace(' ', '_')
    ss = wn.synset_resolver[sense.synsetid]
    pos = PartOfSpeech(ss.pos)
    ss_type = ss_types[pos]
    lex_filenum = lex_file_nums[ss.lex_name]
    if sense.id:
        lex_id = extract_lex_id(sense.id)
    else:
        lex_id = gen_lex_id(entry, sense)
    if pos == PartOfSpeech.ADJECTIVE_SATELLITE:
        h = get_head_word(wn, sense)
        assert h is not None
        head_word, head_id = h
    else:
        head_word = ""
        head_id = ""
    return f'{lemma}%{ss_type:1}:{lex_filenum:02}:{lex_id:02}:{head_word}:{head_id}'


def equal_pos(pos1: PartOfSpeech, pos2: PartOfSpeech) -> bool:
    return (pos1 == pos2
            or pos1 == PartOfSpeech.ADJECTIVE and pos2 == PartOfSpeech.ADJECTIVE_SATELLITE
            or pos2 == PartOfSpeech.ADJECTIVE and pos1 == PartOfSpeech.ADJECTIVE_SATELLITE)


# S T R U C T U R E  (R E L A T I O N S)

def check_symmetry_synset(wn: WordnetModel, synset: Synset) -> None:
    for r in synset.relations:
        t = Synset.Relation.Type(r.relation_type)
        if t in Synset.Relation.inverses:
            t2 = Synset.Relation.inverses[t]
            synset2 = wn.synset_resolver[r.target]
            if not any(r for r in synset2.relations if r.target == synset.id and Synset.Relation.Type(r.relation_type) == t2):
                warn(f'No symmetric relation for {synset.id} ={r.relation_type}=> {synset2.id}')


def check_symmetry_sense(wn: WordnetModel, sense: Sense) -> None:
    for r in sense.relations:
        if not r.other_type:
            t = Sense.Relation.Type(r.relation_type)
            if t in Sense.Relation.inverses:
                t2 = Sense.Relation.inverses[t]
                sense2 = wn.sense_resolver[r.target]
                if not any(r for r in sense2.relations if
                           r.target == sense.id and
                           not r.other_type and
                           Sense.Relation.Type(r.relation_type) == t2):
                    warn(f'No symmetric relation for {sense.id} ={r.relation_type}=> {sense2.id}')


def check_symmetry(wn: WordnetModel) -> None:
    for synset in wn.synsets:
        check_symmetry_synset(wn, synset)
    for sense in wn.senses:
        check_symmetry_sense(wn, sense)


def check_transitive_synset(wn: WordnetModel, synset: Synset) -> None:
    for r1 in synset.relations:
        t1 = Synset.Relation.Type(r1.relation_type)
        if t1 == Synset.Relation.Type.HYPERNYM:
            synset2 = wn.synset_resolver[r1.target]
            for r2 in synset2.relations:
                t2 = Synset.Relation.Type(r2.relation_type)
                if t2 == Synset.Relation.Type.HYPERNYM:
                    if any(r for r in synset.relations if
                           r.target == r2.target and Synset.Relation.Type(r.relation_type) == Synset.Relation.Type.HYPERNYM):
                        trans = next(r for r in synset.relations if
                                     r.target == r2.target and
                                     Synset.Relation.Type(r.relation_type) == Synset.Relation.Type.HYPERNYM)
                        warn(f'Transitive error for {synset.id} => {synset2.id} => {r2.target} with {synset.id} => {trans.target}')


def check_transitive(wn: WordnetModel) -> None:
    for synset in wn.synsets:
        check_transitive_synset(wn, synset)


def check_no_loops(wn: WordnetModel) -> None:
    hypernyms = {}
    for synset in wn.synsets:
        hypernyms[synset.id] = set()
        for r in synset.relations:
            if Synset.Relation.Type(r.relation_type) == Synset.Relation.Type.HYPERNYM:
                hypernyms[synset.id].add(r.target)
    changed = True
    while changed:
        changed = False
        for synset in wn.synsets:
            n_size = len(hypernyms[synset.id])
            for c in hypernyms[synset.id]:
                hypernyms[synset.id] = hypernyms[synset.id].union(hypernyms.get(c, []))
                if synset.id in hypernyms[synset.id]:
                    warn(f'Loop for {synset.id} <-> {c}')
            if len(hypernyms[synset.id]) != n_size:
                changed = True


def check_no_domain_loops(wn: WordnetModel) -> None:
    domains = {}
    for synset in wn.synsets:
        domains[synset.id] = set()
        for r in synset.relations:
            t = Synset.Relation.Type(r.relation_type)
            if t in (Synset.Relation.Type.DOMAIN_TOPIC, Synset.Relation.Type.DOMAIN_REGION, Synset.Relation.Type.EXEMPLIFIES):
                domains[synset.id].add(r.target)
    changed = True
    while changed:
        changed = False
        for synset in wn.synsets:
            n_size = len(domains[synset.id])
            for c in domains[synset.id]:
                domains[synset.id] = domains[synset.id].union(domains.get(c, []))
            if len(domains[synset.id]) != n_size:
                changed = True
            if synset.id in domains[synset.id]:
                warn(f'Domain loop for {synset.id}')


# E N T R I E S

def check_entry_keys(wn) -> None:
    entry_keys = set()
    for entry in wn.entries:
        k = entry.key
        if k in entry_keys:
            warn(f'Duplicate key: {k} for {entry}')
        entry_keys.add(k)


def check_entry_sense_duplicates(entry: Entry) -> None:
    for sense in entry.senses:
        for sense2 in entry.senses:
            if sense2.id != sense.id and sense2.synsetid == sense.synsetid:
                warn(f'Duplicate senses {sense.id} + {sense2.id} both referring to {sense.synsetid}')


def check_entries(wn: WordnetModel) -> None:
    check_entry_keys(wn)
    for e in wn.entries:
        check_entry_sense_duplicates(e)


# S E N S E S

def check_senseid_duplicates(wn: WordnetModel) -> None:
    visited_sense_ids = {}
    for sense in wn.senses:
        if sense.id in visited_sense_ids:
            warn(f'Duplicate sense id {sense.id}')
        visited_sense_ids[sense.id] = sense.id


def check_sense(wn: WordnetModel, sense: Sense) -> None:
    # sense id is present
    if not sense.id:
        warn("Sense %s does not have a sense id" % sense)
    # id is valid
    check_valid_sense_id(sense.id)
    check_valid_sense_id_for_target(sense.id, sense.synsetid)
    # sensekey is well-formed as expected
    calc_sense_key = make_sense_key(wn, sense.entry, sense)
    if sense.id != calc_sense_key:
        warn(f'Sense {sense.id} should have {calc_sense_key} id')
    # synset reference resolves
    try:
        wn.synset_resolver[sense.synsetid]
    except KeyError as _:
        warn(f'Sense {sense.id} refers to nonexistent synset {sense.synsetid}')


def check_sense_relations(wn: WordnetModel, sense: Sense) -> None:
    synset = wn.synset_resolver[sense.synsetid]
    pos = PartOfSpeech(synset.pos)

    # Iterate
    for r in sense.relations:
        if not r.other_type and Sense.Relation.Type(r.relation_type) == Sense.Relation.Type.PERTAINYM:
            if not equal_pos(pos, PartOfSpeech.ADJECTIVE) and not equal_pos(pos, PartOfSpeech.ADVERB):
                warn(f'Pertainym {r.target} of {sense.id} should be between adjectives')

    # Duplicates
    counter = Counter((r.target, r.relation_type) for r in sense.relations)
    for item, count in counter.items():
        if count > 1:
            warn(f'Duplicate relation {sense.id} ={item[1]}=> {item[0]}')


def check_sense_verbframes(sense: Sense) -> None:
    counter = Counter(sense.verbframeids)
    for item, count in counter.items():
        if count > 1:
            warn(f'Duplicate verb frames in entry {sense.id}')


def check_senses(wn: WordnetModel) -> None:
    check_senseid_duplicates(wn)
    for sense in wn.senses:
        check_sense(wn, sense)
        check_sense_relations(wn, sense)
        check_sense_verbframes(sense)


# S Y N S E T S

def check_members(wn: WordnetModel, synset: Synset) -> None:
    if not synset.members:
        warn(f'Synset {synset.id} members empty')
    try:
        for m in synset.members:
            _ = wn.member_resolver[m, synset.id]
    except KeyError as ke:
        warn(f'Synset {synset.id} refers to nonexistent member {ke.args[0]}')


def check_synset_relations(wn: WordnetModel, synset: Synset) -> None:
    pos = PartOfSpeech(synset.pos)

    # Iterate
    for r in synset.relations:
        t = Synset.Relation.Type(r.relation_type)
        # resolve target
        try:
            target = wn.synset_resolver[r.target]
            # cross-pos hypernym
            if t == Synset.Relation.Type.HYPERNYM and not equal_pos(pos, PartOfSpeech(target.pos)):
                warn(f'Cross-part-of-speech hypernym {synset.id} => {r.target}')
            # no synset antonym
            if t == Synset.Relation.Type.ANTONYM:
                warn(f'Antonymy should be at the sense level {synset.id} => {r.target}')
        except KeyError as _:
            warn(f'{synset.id} refers to nonexistent synset {r.target}')

    # Duplicates
    sorted_relations = sorted(synset.relations, key=lambda _: (_.target, _.relation_type))
    for i in range(len(sorted_relations) - 1):
        r = sorted_relations[i]
        r_next = sorted_relations[i + 1]
        if r.target == r_next.target and Synset.Relation.Type(r.relation_type) == Synset.Relation.Type(r_next.relation_type):
            warn(f'Duplicate synset relation {synset.id} ={r.relation_type}=> {r.target}')
    # TODO redundant
    counter = Counter((r.target, r.relation_type) for r in synset.relations)
    for item, count in counter.items():
        if count > 1:
            warn(f'Duplicate synset relation {synset.id} ={item[1]}=> {item[0]}')

    # Similar/ Adj clusters
    def count_similars(ss: Synset):
        result = 0
        for r2 in ss.relations:
            t2 = Synset.Relation.Type(r2.relation_type)
            if t2 == Synset.Relation.Type.SIMILAR:
                if not equal_pos(pos, PartOfSpeech.VERB) and not equal_pos(pos, PartOfSpeech.ADJECTIVE):
                    warn(f'Similar relation not between verb/adjective {ss.id} => {r2.target}')
                result += 1
                if result > 1 and pos == PartOfSpeech.ADJECTIVE_SATELLITE:
                    warn(f'Satellite of more than one synset {ss.id}')
        return result

    if pos == PartOfSpeech.ADJECTIVE_SATELLITE:
        if count_similars(synset) == 0:
            warn(f'Satellite must have at least one similar relation {synset.id}')

    # Noun hypernyms
    top = "00001740-n"
    if pos == PartOfSpeech.NOUN:
        hypernyms = [r for r in synset.relations if
                     Synset.Relation.Type(r.relation_type) == Synset.Relation.Type.HYPERNYM or
                     Synset.Relation.Type(r.relation_type) == Synset.Relation.Type.INSTANCE_HYPERNYM]
        if not hypernyms and synset.id != top:
            warn(f'Noun synset {synset.id} has no hypernym')


def check_instances(wn: WordnetModel) -> None:
    def collect_instances():
        result = set()
        for ss in wn.synsets:
            if any(Synset.Relation.Type(r2.relation_type) == Synset.Relation.Type.INSTANCE_HYPERNYM for r2 in ss.relations):
                if any(Synset.Relation.Type(r3.relation_type) == Synset.Relation.Type.HYPERNYM for r3 in ss.relations):
                    warn(f'Synset {ss.id} has both hypernym and instance hypernym')
                result.add(ss.id)
        return result

    instances = collect_instances()
    for synset in wn.synsets:
        for r in synset.relations:
            if Synset.Relation.Type(r.relation_type) == Synset.Relation.Type.HYPERNYM:
                if r.target in instances:
                    warn(f'Hypernym targets instance {synset.id} => {r.target}')


def check_ili(synset: Synset) -> None:
    if (not synset.ili or synset.ili == "in") and not synset.ili_definition:
        pass  # TODO print("%s does not have an ILI definition" % ss.id)


def check_synset(wn: WordnetModel, synset: Synset) -> None:
    pos = PartOfSpeech(synset.pos)

    # id
    check_valid_synset_id(synset.id)
    if synset.id[-1:] != pos.value:
        warn(f'Synset ID {synset.id} clashes with part-of-speech {pos.value}')
    # members
    check_members(wn, synset)
    # definitions
    if len(synset.definitions) == 0:
        warn(f'Synset without definition {synset.id}')
    for defn in synset.definitions:
        if len(defn) == 0:
            warn('Synset with empty definition {synset.id}')
    # ili
    check_ili(synset)

    # Synset relations
    check_synset_relations(wn, synset)


def check_synsets(wn: WordnetModel) -> None:
    for synset in wn.synsets:
        check_synset(wn, synset)
    check_instances(wn)


def main(wn: WordnetModel) -> None:
    check_entries(wn)

    check_senses(wn)
    check_synsets(wn)

    check_symmetry(wn)
    check_transitive(wn)
    check_no_loops(wn)
    check_no_domain_loops(wn)


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="load from yaml and save")
    arg_parser.add_argument('--pickle', action='store_true', default=False, help='use pickle')
    arg_parser.add_argument('in_dir', type=str, help='from-dir for yaml/pickle')
    arg_parser.add_argument('pickled', type=str, nargs='?', default='oewn.pickle', help='from-pickle')
    args = arg_parser.parse_args()


    def get_wn() -> WordnetModel:
        if args.pickle:
            from oewn_core.deserialize import load as pickle_load
            return pickle_load(args.in_dir, args.pickled) #, extend=True
        from oewn_core.wordnet_fromyaml import load as yaml_load
        return yaml_load(args.in_dir) # , extend=True


    _wn: WordnetModel = get_wn()
    try:
        main(_wn)
        print("No validity issues")
    except ValidationError as ve:
        print(ve, file=sys.stderr)
