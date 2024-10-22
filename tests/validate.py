"""
WordNet model validation
This is validation of model's semantics
This validation does not validate XML form (use an XML validator)

Author: John McCrae <john@mccr.ae> for original code
Author: Bernard Bou <1313ou@gmail.com> for rewrite and revamp
"""

import deserialize
from wordnet import (Synset, Sense, PartOfSpeech, WordnetModel, Entry)
import re
import sys
from collections import Counter

from wordnet_xml import xml_id_char


class ValidationError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


def check_symmetry(wn: WordnetModel):
    for synset in wn.synsets:
        for r in synset.relations:
            t = Synset.Relation.Type(r.relation_type)
            t2 = Synset.Relation.inverses[t]
            if t in Synset.Relation.inverses:
                synset2 = wn.synset_resolver[r.target]
                if not any(r for r in synset2.relations if r.target == synset.id and r.relation_type == t2):
                    pass  # TODO raise ValidationError(f'No symmetric relation for {synset.id} ={r.relation_type}=> {synset2.id}')
    for sense in wn.senses:
        for r in sense.relations:
            if not r.other_type:
                t = Sense.Relation.Type(r.relation_type)
                if t in Sense.Relation.inverses:
                    t2 = Sense.Relation.inverses[t]
                    sense2 = wn.sense_resolver[r.target]
                    if not any(r for r in sense2.relations if
                               r.target == sense.id and
                               r.relation_type == t2):
                        pass  # TODO raise ValidationError(f'No symmetric relation for {sense.id} ={r.relation_type}=> {sense2.id}')


def check_transitive(wn: WordnetModel):
    for synset in wn.synsets:
        for r in synset.relations:
            t = Synset.Relation.Type(r.relation_type)
            if t == Synset.Relation.Type.HYPERNYM:
                synset2 = wn.synset_resolver[r.target]
                for r2 in synset2.relations:
                    t2 = Synset.Relation.Type(r2.relation_type)
                    if (any(r for r in synset.relations if
                            r.target == r2.target and
                            t == Synset.Relation.Type.HYPERNYM) and
                            t2 == Synset.Relation.Type.HYPERNYM):
                        pass  # TODO raise ValidationError(f'Transitive error for {synset.id} => {synset2.id} => {r2.target}')


def check_no_loops(wn: WordnetModel):
    hypernyms = {}
    for synset in wn.synsets:
        hypernyms[synset.id] = set()
        for r in synset.relations:
            if r.relation_type == Synset.Relation.Type.HYPERNYM:
                hypernyms[synset.id].add(r.target)
    changed = True
    while changed:
        changed = False
        for synset in wn.synsets:
            n_size = len(hypernyms[synset.id])
            for c in hypernyms[synset.id]:
                hypernyms[synset.id] = hypernyms[synset.id].union(hypernyms.get(c, []))
                if synset.id in hypernyms[synset.id]:
                    return ["Loop for %s <-> %s" % (synset.id, c)]
            if len(hypernyms[synset.id]) != n_size:
                changed = True
    return []


def check_no_domain_loops(wn: WordnetModel):
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
                raise ValidationError([f'Domain loop for {synset.id}'])


def check_members(wn: WordnetModel, synset: Synset):
    return [wn.member_resolver[m, synset.id] for m in synset.members]


def check_ili(synset: Synset):
    if (not synset.ili or synset.ili == "in") and not synset.ili_definition:
        pass  # TODO print("%s does not have an ILI definition" % ss.id)


def check_lex_files(wn: WordnetModel):
    for entry in wn.entries:
        for sense in entry.senses:
            if not sense.id:
                raise ValidationError("%s does not have a sense key" % sense.id)
            if not wn.synset_resolver[sense.synsetid]:
                raise ValidationError(f'{sense.id} refers to nonexistent synset {sense.synsetid}')
            calc_sense_key = get_sense_key(wn, entry, sense)
            if sense.id != calc_sense_key:
                raise ValidationError(f'Sense {sense.id} should have {calc_sense_key} id')


valid_id = re.compile(fr"^{xml_id_char}*$")

valid_sense_id = re.compile("^[A-Za-z0-9_\\-.]+-([nvars])-([0-9]{8})-[0-9]{2}$")

valid_synset_id = re.compile("^[0-9]{8}-[nvars]$")


def is_valid_id(any_id: str):
    return bool(valid_id.match(any_id))


def is_valid_synset_id(synset_id: str):
    return bool(valid_synset_id.match(synset_id))


# TODO
def is_valid_sense_id(sense_id: str, target_id: str):
    m = valid_sense_id.match(sense_id)
    if not m:
        raise ValidationError(f'{sense_id} is not well-formed')
    pos = m.group(1)
    key = m.group(2)
    if target_id != f'{key}-{pos}':
        raise ValidationError(f'{target_id} target of {sense_id} is not well-formed')
    return True


lex_filenums = {
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

ss_types = {
    PartOfSpeech.NOUN: 1,
    PartOfSpeech.VERB: 2,
    PartOfSpeech.ADJECTIVE: 3,
    PartOfSpeech.ADVERB: 4,
    PartOfSpeech.ADJECTIVE_SATELLITE: 5
}

sense_id_lex_id = re.compile(".*%\\d:\\d\\d:(\\d\\d):.*")


def gen_lex_id(entry: Entry, sense: Sense):
    max_id = 0
    unseen = 1
    seen = False
    for s2 in entry.senses:
        if s2.id:
            m = re.match(sense_id_lex_id, s2.id)
            max_id = max(max_id, int(m.group(1)))
        else:
            if not seen:
                if s2.id == sense.id:
                    seen = True
                else:
                    unseen += 1
    return max_id + unseen


def extract_lex_id(sense_key: str):
    return int(re.match(sense_id_lex_id, sense_key).group(1))


def get_head_word(wn: WordnetModel, sense: Sense):
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
        head = target_sense.id[:target_sense.id.rindex('%')]
        head_id = re.match(sense_id_lex_id, target_sense.id).group(1)
        return head, head_id
    raise ValidationError(f'Could not deduce target of satellite {sense.id}')


def get_sense_key(wn: WordnetModel, entry: Entry, sense: Sense):
    """Calculate the sense key for a sense of an entry"""
    lemma = entry.lemma.lower().replace(' ', '_')
    ss = wn.synset_resolver[sense.synsetid]
    pos = PartOfSpeech(ss.pos)
    ss_type = ss_types[pos]
    lex_filenum = lex_filenums[ss.lex_name]
    if sense.id:
        lex_id = extract_lex_id(sense.id)
    else:
        lex_id = gen_lex_id(entry, sense)
    if pos == PartOfSpeech.ADJECTIVE_SATELLITE:
        head_word, head_id = get_head_word(wn, sense)
    else:
        head_word = ""
        head_id = ""
    return f'{lemma}%{ss_type:1}:{lex_filenum:02}:{lex_id:02}:{head_word}:{head_id}'


def equal_pos(pos1: PartOfSpeech, pos2: PartOfSpeech):
    return (pos1 == pos2
            or pos1 == PartOfSpeech.ADJECTIVE and pos2 == PartOfSpeech.ADJECTIVE_SATELLITE
            or pos2 == PartOfSpeech.ADJECTIVE and pos1 == PartOfSpeech.ADJECTIVE_SATELLITE)


# s e n s e s

def scan_senses(wn: WordnetModel):
    visited_sense_ids = {}
    for entry in wn.entries:
        for sense in entry.senses:

            if sense.id in visited_sense_ids:
                raise ValidationError(f'Duplicate sense id {sense.id}')  # later caught by XML validator

            visited_sense_ids[sense.id] = sense.id

            synset = wn.synset_resolver[sense.synsetid]
            pos = PartOfSpeech(synset.pos)

            for r in sense.relations:
                if not r.other_type and Sense.Relation.Type(r.relation_type) == Sense.Relation.Type.PERTAINYM:
                    if not equal_pos(pos, PartOfSpeech.ADJECTIVE) and not equal_pos(pos, PartOfSpeech.ADVERB):
                        raise ValidationError(f'Pertainym {r.target} of {sense.id} should be between adjectives')

            sr_counter = Counter((r.target, r.relation_type) for r in sense.relations)
            for item, count in sr_counter.items():
                if count > 1:
                    raise ValidationError(f'Duplicate relation {sense.id} ={item[1]}=> {item[0]}')

            sb_counter = Counter(sense.verbframeids)
            for item, count in sb_counter.items():
                if count > 1:
                    raise ValidationError(f'Duplicate syntactic behaviour in entry {entry.key}')

            for sense2 in entry.senses:
                if sense2.id != sense.id and sense2.synsetid == sense.synsetid:
                    raise ValidationError(f'Duplicate senses {sense.id} + {sense2.id} referring to {sense.synsetid}')


# s y n s e t s

def scan_synsets(wn: WordnetModel):
    instances = set()
    for synset in wn.synsets:
        pos = PartOfSpeech(synset.pos)

        if synset.id[-1:] != pos.value:
            raise ValidationError(f'Synset ID {synset.id} clashes with part-of-speech {pos.value}')
        if not is_valid_synset_id(synset.id):
            raise ValidationError(f'Invalid ID {synset.id}')
        if not check_members(wn, synset):
            raise ValidationError(f'Synset {synset.id} members empty')

        if len(synset.definitions) == 0:
            raise ValidationError(f'Synset without definition {synset.id}')
        for defn in synset.definitions:
            if len(defn) == 0:
                raise ValidationError('Synset with empty definition {synset.id}')

        check_ili(synset)

        # Duplicate synset relation
        sorted_relations = sorted(synset.relations, key=lambda _: (_.target, _.relation_type))
        for i in range(len(sorted_relations) - 1):
            r = sorted_relations[i]
            r_next = sorted_relations[i + 1]
            if r.target == r_next.target and r.relation_type == r_next.relation_type:
                raise ValidationError(f'Duplicate synset relation {synset.id} ={r.relation_type}=> {r.target}')

        # Synset relations
        for r in synset.relations:
            t = Synset.Relation.Type(r.relation_type)
            target = wn.synset_resolver[r.target]

            if t == Synset.Relation.Type.HYPERNYM and not equal_pos(pos, PartOfSpeech(target.pos)):
                raise ValidationError(f'Cross-part-of-speech hypernym {synset.id} => {r.target}')

            if t == Synset.Relation.Type.ANTONYM:
                raise ValidationError(f'antonymy should be at the sense level {synset.id} => {r.target}')

        # Similar
        similars = 0
        for r in synset.relations:
            t = Synset.Relation.Type(r.relation_type)
            if t == Synset.Relation.Type.SIMILAR:
                if not equal_pos(pos, PartOfSpeech.VERB) and not equal_pos(pos, PartOfSpeech.ADJECTIVE):
                    raise ValidationError(f'similar not between verb/adjective {synset.id} => {r.target}')
                similars += 1
                if similars > 1 and pos == PartOfSpeech.ADJECTIVE_SATELLITE:
                    raise ValidationError(f'satellite of more than one synset {synset.id}')
        if pos == PartOfSpeech.ADJECTIVE_SATELLITE and similars == 0:
            raise ValidationError(f'satellite must have at least one similar link {synset.id}')

        # Noun hypernyms
        if pos == PartOfSpeech.NOUN:
            hypernyms = [r for r in synset.relations if
                         Synset.Relation.Type(r.relation_type) == Synset.Relation.Type.HYPERNYM or
                         Synset.Relation.Type(r.relation_type) == Synset.Relation.Type.INSTANCE_HYPERNYM]
            if not hypernyms and synset.id != "00001740-n":
                raise ValidationError(f'noun synset {synset.id} has no hypernym')

        if any(Synset.Relation.Type(r.relation_type) == Synset.Relation.Type.INSTANCE_HYPERNYM for r in synset.relations):
            if any(Synset.Relation.Type(r.relation_type) == Synset.Relation.Type.HYPERNYM for r in synset.relations):
                raise ValidationError(f'synset {synset.id} has both hypernym and instance hypernym')
            instances.add(synset.id)

        sr_counter = Counter((r.target, r.relation_type) for r in synset.relations)
        for item, count in sr_counter.items():
            if count > 1:
                raise ValidationError(f'Duplicate relation {synset.id} ={item[1]}=> {item[0]}')

    for synset in wn.synsets:
        for r in synset.relations:
            if r.relation_type == Synset.Relation.Type.HYPERNYM:
                if r.target in instances:
                    raise ValidationError(f'Hypernym targets instance {synset.id} => {r.target}')


def main(wn: WordnetModel):
    check_lex_files(wn)

    scan_senses(wn)
    scan_synsets(wn)

    check_symmetry(wn)
    check_transitive(wn)
    check_no_loops(wn)
    check_no_domain_loops(wn)


if __name__ == "__main__":
    pickled_wn = deserialize.main()
    pickled_wn.extend()
    try:
        main(pickled_wn)
        print("No validity issues")
    except ValidationError as e:
        print(e, file=sys.stderr)
