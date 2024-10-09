"""
WordNet model

Author: John McCrae <john@mccr.ae> for original code
Author: Bernard Bou <1313ou@gmail.com> for rewrite and revamp
"""

#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

from enum import Enum
from typing import List, Dict, Tuple, Optional


class Entry:
    """The lexical entry consists of a single word"""

    def __init__(self, lemma, pos, discriminant):
        self.lemma: str = lemma
        self.pos: str = pos
        self.discriminant: str = discriminant
        self.forms: List[str] = []
        self.pronunciations: List[Pronunciation] = []
        self.senses: List[Sense] = []


class Sense:
    """ The sense links an entry to a synset """

    def __init__(self, senseid, entry, synsetid, n=None, adjposition=None):
        self.id: str = senseid
        self.entry: Entry = entry
        self.synsetid: str = synsetid
        self.resolved_synset: Optional[Synset] = None
        self.n: int = n
        self.adjposition: Optional[str] = adjposition
        self.verbframeids: Optional[List[str]] = None
        self.sent: Optional[str] = None
        self.relations: List[Sense.Relation] = []

    def __getstate__(self):
        state = self.__dict__.copy()
        if 'resolved_synset' in state:
            del state['resolved_synset']  # exclude from being pickled
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.resolved_synset = None  # restore o a default or None value

    class Relation:
        """ Lexical relation (sense to sense)"""

        class Type(Enum):
            ANTONYM = 'antonym'
            ALSO = 'also'
            PARTICIPLE = 'participle'
            PERTAINYM = 'pertainym'
            DERIVATION = 'derivation'
            DOMAIN_TOPIC = 'domain_topic'
            HAS_DOMAIN_TOPIC = 'has_domain_topic'
            DOMAIN_REGION = 'domain_region'
            HAS_DOMAIN_REGION = 'has_domain_region'
            EXEMPLIFIES = 'exemplifies'
            IS_EXEMPLIFIED_BY = 'is_exemplified_by'
            SIMILAR = 'similar'
            OTHER = 'other'

        inverses: Dict[Type, Type] = {
            Type.DOMAIN_REGION: Type.HAS_DOMAIN_REGION,
            Type.HAS_DOMAIN_REGION: Type.DOMAIN_REGION,
            Type.DOMAIN_TOPIC: Type.HAS_DOMAIN_TOPIC,
            Type.HAS_DOMAIN_TOPIC: Type.DOMAIN_TOPIC,
            Type.EXEMPLIFIES: Type.IS_EXEMPLIFIED_BY,
            Type.IS_EXEMPLIFIED_BY: Type.EXEMPLIFIES,
            Type.ANTONYM: Type.ANTONYM,
            Type.SIMILAR: Type.SIMILAR,
            Type.ALSO: Type.ALSO,
            Type.DERIVATION: Type.DERIVATION,
        }

        class OtherType(Enum):
            AGENT = 'agent'
            MATERIAL = 'material'
            EVENT = 'event'
            INSTRUMENT = 'instrument'
            LOCATION = 'location'
            BY_MEANS_OF = 'by_means_of'
            UNDERGOER = 'undergoer'
            PROPERTY = 'property'
            RESULT = 'result'
            STATE = 'state'
            USES = 'uses'
            DESTINATION = 'destination'
            BODY_PART = 'body_part'
            VEHICLE = 'vehicle'

        def __init__(self, target, relation_type, other_type=False):
            self.target: str = target
            self.resolved_target: Optional[Sense] = None
            self.relation_type: str = relation_type
            self.other_type: bool = other_type

        def __getstate__(self):
            state = self.__dict__.copy()
            if 'resolved_target' in state:
                del state['resolved_target']  # exclude from being pickled
            return state

        def __setstate__(self, state):
            self.__dict__.update(state)
            self.resolved_target = None  # restore o a default or None value


class Synset:
    """ Synset, a collection of members that share a common meaning """

    def __init__(self, synsetid, pos, members, lex_name):
        self.id: str = synsetid
        self.pos: str = PartOfSpeech(pos).value
        self.members: List[str] = members
        self.resolved_members: Optional[List, Entry] = None
        self.lex_name: str = lex_name
        self.definitions: List[str] = []
        self.examples: List[str | Example] = []
        self.usages: List[str] = []
        self.relations: List[Synset.Relation] = []
        self.ili_definition: Optional[str] = None
        self.source: Optional[str] = None
        self.wikidata: Optional[str] = None
        self.ili: Optional[str] = None

    def __getstate__(self):
        state = self.__dict__.copy()
        if 'resolved_members' in state:
            del state['resolved_members']  # exclude from being pickled
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.resolved_members = None  # restore o a default or None value

    class Relation:
        """ Semantic relation (synset to synset)"""

        class Type(Enum):
            AGENT = 'agent'
            ALSO = 'also'
            ATTRIBUTE = 'attribute'
            BE_IN_STATE = 'be_in_state'
            CAUSES = 'causes'
            CLASSIFIED_BY = 'classified_by'
            CLASSIFIES = 'classifies'
            CO_AGENT_INSTRUMENT = 'co_agent_instrument'
            CO_AGENT_PATIENT = 'co_agent_patient'
            CO_AGENT_RESULT = 'co_agent_result'
            CO_INSTRUMENT_AGENT = 'co_instrument_agent'
            CO_INSTRUMENT_PATIENT = 'co_instrument_patient'
            CO_INSTRUMENT_RESULT = 'co_instrument_result'
            CO_PATIENT_AGENT = 'co_patient_agent'
            CO_PATIENT_INSTRUMENT = 'co_patient_instrument'
            CO_RESULT_AGENT = 'co_result_agent'
            CO_RESULT_INSTRUMENT = 'co_result_instrument'
            CO_ROLE = 'co_role'
            DIRECTION = 'direction'
            DOMAIN_REGION = 'domain_region'
            DOMAIN_TOPIC = 'domain_topic'
            EXEMPLIFIES = 'exemplifies'
            ENTAILS = 'entails'
            EQ_SYNONYM = 'eq_synonym'
            HAS_DOMAIN_REGION = 'has_domain_region'
            HAS_DOMAIN_TOPIC = 'has_domain_topic'
            IS_EXEMPLIFIED_BY = 'is_exemplified_by'
            HOLO_LOCATION = 'holo_location'
            HOLO_MEMBER = 'holo_member'
            HOLO_PART = 'holo_part'
            HOLO_PORTION = 'holo_portion'
            HOLO_SUBSTANCE = 'holo_substance'
            HOLONYM = 'holonym'
            HYPERNYM = 'hypernym'
            HYPONYM = 'hyponym'
            IN_MANNER = 'in_manner'
            INSTANCE_HYPERNYM = 'instance_hypernym'
            INSTANCE_HYPONYM = 'instance_hyponym'
            INSTRUMENT = 'instrument'
            INVOLVED = 'involved'
            INVOLVED_AGENT = 'involved_agent'
            INVOLVED_DIRECTION = 'involved_direction'
            INVOLVED_INSTRUMENT = 'involved_instrument'
            INVOLVED_LOCATION = 'involved_location'
            INVOLVED_PATIENT = 'involved_patient'
            INVOLVED_RESULT = 'involved_result'
            INVOLVED_SOURCE_DIRECTION = 'involved_source_direction'
            INVOLVED_TARGET_DIRECTION = 'involved_target_direction'
            IS_CAUSED_BY = 'is_caused_by'
            IS_ENTAILED_BY = 'is_entailed_by'
            LOCATION = 'location'
            MANNER_OF = 'manner_of'
            MERO_LOCATION = 'mero_location'
            MERO_MEMBER = 'mero_member'
            MERO_PART = 'mero_part'
            MERO_PORTION = 'mero_portion'
            MERO_SUBSTANCE = 'mero_substance'
            MERONYM = 'meronym'
            SIMILAR = 'similar'
            OTHER = 'other'
            PATIENT = 'patient'
            RESTRICTED_BY = 'restricted_by'
            RESTRICTS = 'restricts'
            RESULT = 'result'
            ROLE = 'role'
            SOURCE_DIRECTION = 'source_direction'
            STATE_OF = 'state_of'
            TARGET_DIRECTION = 'target_direction'
            SUBEVENT = 'subevent'
            IS_SUBEVENT_OF = 'is_subevent_of'
            ANTONYM = 'antonym'

        inverses: Dict[Type, Type] = {
            Type.HYPERNYM: Type.HYPONYM,
            Type.HYPONYM: Type.HYPERNYM,
            Type.INSTANCE_HYPERNYM: Type.INSTANCE_HYPONYM,
            Type.INSTANCE_HYPONYM: Type.INSTANCE_HYPERNYM,
            Type.MERONYM: Type.HOLONYM,
            Type.HOLONYM: Type.MERONYM,
            Type.MERO_LOCATION: Type.HOLO_LOCATION,
            Type.HOLO_LOCATION: Type.MERO_LOCATION,
            Type.MERO_MEMBER: Type.HOLO_MEMBER,
            Type.HOLO_MEMBER: Type.MERO_MEMBER,
            Type.MERO_PART: Type.HOLO_PART,
            Type.HOLO_PART: Type.MERO_PART,
            Type.MERO_PORTION: Type.HOLO_PORTION,
            Type.HOLO_PORTION: Type.MERO_PORTION,
            Type.MERO_SUBSTANCE: Type.HOLO_SUBSTANCE,
            Type.HOLO_SUBSTANCE: Type.MERO_SUBSTANCE,
            Type.BE_IN_STATE: Type.STATE_OF,
            Type.STATE_OF: Type.BE_IN_STATE,
            Type.CAUSES: Type.IS_CAUSED_BY,
            Type.IS_CAUSED_BY: Type.CAUSES,
            Type.SUBEVENT: Type.IS_SUBEVENT_OF,
            Type.IS_SUBEVENT_OF: Type.SUBEVENT,
            Type.MANNER_OF: Type.IN_MANNER,
            Type.IN_MANNER: Type.MANNER_OF,
            Type.RESTRICTS: Type.RESTRICTED_BY,
            Type.RESTRICTED_BY: Type.RESTRICTS,
            Type.CLASSIFIES: Type.CLASSIFIED_BY,
            Type.CLASSIFIED_BY: Type.CLASSIFIES,
            Type.ENTAILS: Type.IS_ENTAILED_BY,
            Type.IS_ENTAILED_BY: Type.ENTAILS,
            Type.DOMAIN_REGION: Type.HAS_DOMAIN_REGION,
            Type.HAS_DOMAIN_REGION: Type.DOMAIN_REGION,
            Type.DOMAIN_TOPIC: Type.HAS_DOMAIN_TOPIC,
            Type.HAS_DOMAIN_TOPIC: Type.DOMAIN_TOPIC,
            Type.EXEMPLIFIES: Type.IS_EXEMPLIFIED_BY,
            Type.IS_EXEMPLIFIED_BY: Type.EXEMPLIFIES,
            Type.ROLE: Type.INVOLVED,
            Type.INVOLVED: Type.ROLE,
            Type.AGENT: Type.INVOLVED_AGENT,
            Type.INVOLVED_AGENT: Type.AGENT,
            Type.PATIENT: Type.INVOLVED_PATIENT,
            Type.INVOLVED_PATIENT: Type.PATIENT,
            Type.RESULT: Type.INVOLVED_RESULT,
            Type.INVOLVED_RESULT: Type.RESULT,
            Type.INSTRUMENT: Type.INVOLVED_INSTRUMENT,
            Type.INVOLVED_INSTRUMENT: Type.INSTRUMENT,
            Type.LOCATION: Type.INVOLVED_LOCATION,
            Type.INVOLVED_LOCATION: Type.LOCATION,
            Type.DIRECTION: Type.INVOLVED_DIRECTION,
            Type.INVOLVED_DIRECTION: Type.DIRECTION,
            Type.TARGET_DIRECTION: Type.INVOLVED_TARGET_DIRECTION,
            Type.INVOLVED_TARGET_DIRECTION: Type.TARGET_DIRECTION,
            Type.SOURCE_DIRECTION: Type.INVOLVED_SOURCE_DIRECTION,
            Type.INVOLVED_SOURCE_DIRECTION: Type.SOURCE_DIRECTION,
            Type.CO_AGENT_PATIENT: Type.CO_PATIENT_AGENT,
            Type.CO_PATIENT_AGENT: Type.CO_AGENT_PATIENT,
            Type.CO_AGENT_INSTRUMENT: Type.CO_INSTRUMENT_AGENT,
            Type.CO_INSTRUMENT_AGENT: Type.CO_AGENT_INSTRUMENT,
            Type.CO_AGENT_RESULT: Type.CO_RESULT_AGENT,
            Type.CO_RESULT_AGENT: Type.CO_AGENT_RESULT,
            Type.CO_PATIENT_INSTRUMENT: Type.CO_INSTRUMENT_PATIENT,
            Type.CO_INSTRUMENT_PATIENT: Type.CO_PATIENT_INSTRUMENT,
            Type.CO_RESULT_INSTRUMENT: Type.CO_INSTRUMENT_RESULT,
            Type.CO_INSTRUMENT_RESULT: Type.CO_RESULT_INSTRUMENT,
            Type.ANTONYM: Type.ANTONYM,
            Type.EQ_SYNONYM: Type.EQ_SYNONYM,
            Type.SIMILAR: Type.SIMILAR,
            Type.ALSO: Type.ALSO,
            Type.ATTRIBUTE: Type.ATTRIBUTE,
            Type.CO_ROLE: Type.CO_ROLE
        }

        def __init__(self, target, relation_type):
            self.target: str = target
            self.resolved_target: Optional[Synset] = None
            self.relation_type: str = relation_type

        def __getstate__(self):
            state = self.__dict__.copy()
            if 'resolved_target' in state:
                del state['resolved_target']  # exclude from being pickled
            return state

        def __setstate__(self, state):
            self.__dict__.update(state)
            self.resolved_target = None  # restore o a default or None value


class Pronunciation:
    """ Pronunciation of a lemma"""

    def __init__(self, value, variety=None):
        self.value: str = value
        self.variety: Optional[str] = variety


class Example:
    """ Sourced example """

    def __init__(self, text, source=None):
        self.text: str = text
        self.source: Optional[str] = source


class VerbFrame:
    """ Verb frame """

    def __init__(self, fid, verbframe):
        self.id: str = fid
        self.verbframe: str = verbframe


class PartOfSpeech(Enum):
    """ Parts of speech """

    NOUN = 'n'
    VERB = 'v'
    ADJECTIVE = 'a'
    ADVERB = 'r'
    ADJECTIVE_SATELLITE = 's'


class WordnetModel:
    """
    The Model/Lexicon contains all the synsets and entries
    """

    def __init__(self, lexicon_id, label, language, email, wnlicense, version, url):

        # meta data
        self.id: str = lexicon_id
        self.label: str = label
        self.language: str = language
        self.email: str = email
        self.license: str = wnlicense
        self.version: str = version
        self.url: str = url

        # data
        self.entries: List[Entry] = []
        self.synsets: List[Synset] = []
        self.verbframes: List[VerbFrame] = []

        # resolvers
        self.synset_resolver: Dict[str, Synset] = {}
        self.sense_resolver: Dict[str, Sense] = {}
        self.member_resolver: Dict[Tuple[str, str], Entry] = {}  # key is (lemma,synsetid)

    def __str__(self):
        return f"Wordnet '{self.id}'"

    def info(self):
        """ Counts """
        return f'{self} has {len(self.entries)} entries, {len(self.synsets)} synsets and {sum(1 for _ in self.senses)} senses'

    def info_relations(self):
        """ Counts of relations """
        return f'{self} has {sum(1 for _ in self.sense_relations)} sense relations and {sum(1 for _ in self.synset_relations)} synset relations'

    @property
    def senses(self):
        """ Senses generator """
        for e in self.entries:
            for s in e.senses:
                yield s

    @property
    def sense_relations(self):
        """ Sense relations generator """
        for s in self.senses:
            yield s

    @property
    def synset_relations(self):
        """ Synset relations generator """
        for e in self.entries:
            for s in e.senses:
                yield s

    @property
    def verbframe_resolver(self) -> Dict[str, str]:
        """ Verb frame resolver factory from id """
        return {f.id: f.verbframe for f in self.verbframes}

    def extend(self):
        """
        Extend to include inverse relations can be added here
        """
        # raise NotImplementedError(f'Extending {wn} not implemented')
        for ss in self.synsets:
            self.extend_synset_relations(ss)
        for s in self.senses:
            self.extend_sense_relations(s)

    def extend_sense_relations(self, sense: Sense):
        """
        Add inverse sense relations as needed
        :param sense: sense to extend
        """
        for rel in sense.relations:
            t = rel.relation_type
            if t in Sense.Relation.inverses:
                inv_t = Sense.Relation.inverses[Sense.Relation.Type(t)]
                if inv_t != t:
                    target_sense = self.sense_resolver[rel.target]
                    if not target_sense:
                        raise ValueError(f'Unresolved target {rel.target} in relation of type {t} in sense {sense.id}')
                    if not any(r for r in target_sense.relations if r.target == sense.id and r.relation_type == inv_t):
                        target_sense.relations.append(Sense.Relation(sense.id, inv_t))

    def extend_synset_relations(self, synset: Synset):
        """
        Add inverse synset relations as needed
        :param synset: synset to extend
        """
        for r in synset.relations:
            t = r.relation_type
            if t in Synset.Relation.inverses:
                inv_t = Synset.Relation.inverses[Synset.Relation.Type(t)]
                if inv_t != t:
                    target_synset = self.synset_resolver[r.target]
                    if not target_synset:
                        raise ValueError(f'Unresolved target {r.target} in relation of type {t} in synset {synset.id}')
                    if not any(r for r in target_synset.relations if r.target == synset.id and r.relation_type == inv_t):
                        target_synset.relations.append(Synset.Relation(synset.id, inv_t))

    def resolve(self):
        """
        Resolve model internal cross-references.
        Side effect is computation of resolved_* fields.
        :raises: ValueError when the resolvers are not available
        :raises: KeyError when the resolvers can't resolve the keys
        """
        # sanity check
        if not self.synset_resolver:
            raise ValueError(f'{self} has no synset resolver')
        if not self.sense_resolver:
            raise ValueError(f'{self} has no sense resolver')
        if not self.member_resolver:
            raise ValueError(f'{self} has no member resolver')

        for s in self.senses:
            # resolve synset reference in sense
            s.resolved_synset = self.synset_resolver[s.synsetid]

            for r in s.relations:
                # resolve relation target reference in sense relation
                r.resolved_target = self.sense_resolver[r.target]

        for ss in self.synsets:
            # resolve member references in synset
            ss.resolved_members = [self.member_resolver[(m, ss.id)] for m in ss.members]

            for r in ss.relations:
                # resolve relation target reference in synset relation
                r.resolved_target = self.synset_resolver[r.target]

    def stale(self):
        """
        Stale all model internal cross-references.
        """
        for s in self.senses:
            s.resolved_synset = None
            for r in s.relations:
                r.resolved_target = None
        for ss in self.synsets:
            ss.resolved_members = None
            for r in ss.relations:
                r.resolved_target = None
