"""
WordNet model

Author: John McCrae <john@mccr.ae> for original code
Author: Bernard Bou <1313ou@gmail.com> for rewrite and revamp
"""

#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

from enum import StrEnum, Enum
from typing import Any, Optional, Tuple, List, Dict, Set, Generator


class Entry:
    """The lexical entry consists of a single word"""

    def __init__(self, lemma, pos, discriminant) -> None:
        self.lemma: str = lemma
        self.pos: str = pos
        self.discriminant: str | None = discriminant
        self.forms: List[str] = []
        self.pronunciations: List[Pronunciation] = []
        self.senses: List[Sense] = []

    def __str__(self) -> str:
        return f'{self.lemma},{self.pos}'

    def __repr__(self) -> str:
        return str(self.key)

    @property
    def key(self) -> Tuple[str, str, str | None]:
        return self.lemma, self.pos, self.discriminant


class Sense:
    """ The sense links an entry to a synset """

    def __init__(self, senseid, entry, synsetid, adjposition=None) -> None:
        self.id: str = senseid
        self.entry: Entry = entry
        self.synsetid: str = synsetid
        self.resolved_synset: Optional[Synset] = None
        self.adjposition: Optional[str] = adjposition
        self.examples: List[str] = []
        self.verbframeids: Optional[List[str]] = None
        self.relations: List[Sense.Relation] = []

    def __str__(self) -> str:
        return f'{self.id}'

    def __repr__(self) -> str:
        return f'{self.id} @{self.synsetid}'

    def __getstate__(self) -> Dict[str, Any]:
        state = self.__dict__.copy()
        if 'resolved_synset' in state:
            del state['resolved_synset']  # exclude from being pickled
        return state

    def __setstate__(self, state) -> None:
        self.__dict__.update(state)
        self.resolved_synset = None  # restore o a default or None value

    class Relation:
        """ Lexical relation (sense to sense)"""

        class Type(StrEnum):
            ANTONYM: str = 'antonym'
            ALSO: str = 'also'
            PARTICIPLE: str = 'participle'
            PERTAINYM: str = 'pertainym'
            DERIVATION: str = 'derivation'
            DOMAIN_TOPIC: str = 'domain_topic'
            HAS_DOMAIN_TOPIC: str = 'has_domain_topic'
            DOMAIN_REGION: str = 'domain_region'
            HAS_DOMAIN_REGION: str = 'has_domain_region'
            EXEMPLIFIES: str = 'exemplifies'
            IS_EXEMPLIFIED_BY: str = 'is_exemplified_by'
            SIMILAR: str = 'similar'
            COLLOCATION: str = 'collocation'
            OTHER: str = 'other'

        inverses: Dict[Type, Type] = {
            Type.DOMAIN_REGION: Type.HAS_DOMAIN_REGION,
            Type.HAS_DOMAIN_REGION: Type.DOMAIN_REGION,
            Type.DOMAIN_TOPIC: Type.HAS_DOMAIN_TOPIC,
            Type.HAS_DOMAIN_TOPIC: Type.DOMAIN_TOPIC,
            Type.EXEMPLIFIES: Type.IS_EXEMPLIFIED_BY,
            Type.IS_EXEMPLIFIED_BY: Type.EXEMPLIFIES,
            Type.ANTONYM: Type.ANTONYM,
            Type.SIMILAR: Type.SIMILAR,
            Type.COLLOCATION: Type.COLLOCATION,
            Type.ALSO: Type.ALSO,
            Type.DERIVATION: Type.DERIVATION,
        }

        class OtherType(StrEnum):
            AGENT: str = 'agent'
            MATERIAL: str = 'material'
            EVENT: str = 'event'
            INSTRUMENT: str = 'instrument'
            LOCATION: str = 'location'
            BY_MEANS_OF: str = 'by_means_of'
            UNDERGOER: str = 'undergoer'
            PROPERTY: str = 'property'
            RESULT: str = 'result'
            STATE: str = 'state'
            USES: str = 'uses'
            DESTINATION: str = 'destination'
            BODY_PART: str = 'body_part'
            VEHICLE: str = 'vehicle'

        def __init__(self, target, relation_type, other_type=False) -> None:
            self.target: str = target
            self.resolved_target: Optional[Sense] = None
            self.relation_type: str = relation_type
            self.other_type: bool = other_type

        def __str__(self) -> str:
            return f'-{self.relation_type}-> {self.target}'

        def __repr__(self) -> str:
            return f'{self.relation_type}: {self.target}'

        def __getstate__(self) -> dict[str, Any]:
            state = self.__dict__.copy()
            if 'resolved_target' in state:
                del state['resolved_target']  # exclude from being pickled
            return state

        def __setstate__(self, state) -> None:
            self.__dict__.update(state)
            self.resolved_target = None  # restore o a default or None value


class Synset:
    """ Synset, a collection of members that share a common meaning """

    def __init__(self, synsetid, pos, members, lex_name) -> None:
        self.id: str = synsetid
        self.pos: str = PartOfSpeech(pos).value
        self.members: List[str] = members
        self.resolved_members: Optional[List[Entry]] = None
        self.lex_name: str = lex_name
        self.definitions: List[str] = []
        self.examples: List[str | Example] = []
        self.usages: List[str] = []
        self.ili_definition: Optional[str] = None
        self.source: Optional[str] = None
        self.wikidata: Optional[str] = None
        self.ili: Optional[str] = None
        self.relations: List[Synset.Relation] = []

    def __str__(self) -> str:
        return f'{self.id}'

    def __repr__(self) -> str:
        return f'{self.id} [{' '.join(self.members)}]'

    def __getstate__(self) -> Dict[str, Any]:
        state = self.__dict__.copy()
        if 'resolved_members' in state:
            del state['resolved_members']  # exclude from being pickled
        return state

    def __setstate__(self, state) -> None:
        self.__dict__.update(state)
        self.resolved_members = None  # restore o a default or None value

    class Relation:
        """ Semantic relation (synset to synset)"""

        class Type(StrEnum):
            AGENT: str = 'agent'
            ALSO: str = 'also'
            ATTRIBUTE: str = 'attribute'
            BE_IN_STATE: str = 'be_in_state'
            CAUSES: str = 'causes'
            CLASSIFIED_BY: str = 'classified_by'
            CLASSIFIES: str = 'classifies'
            CO_AGENT_INSTRUMENT: str = 'co_agent_instrument'
            CO_AGENT_PATIENT: str = 'co_agent_patient'
            CO_AGENT_RESULT: str = 'co_agent_result'
            CO_INSTRUMENT_AGENT: str = 'co_instrument_agent'
            CO_INSTRUMENT_PATIENT: str = 'co_instrument_patient'
            CO_INSTRUMENT_RESULT: str = 'co_instrument_result'
            CO_PATIENT_AGENT: str = 'co_patient_agent'
            CO_PATIENT_INSTRUMENT: str = 'co_patient_instrument'
            CO_RESULT_AGENT: str = 'co_result_agent'
            CO_RESULT_INSTRUMENT: str = 'co_result_instrument'
            CO_ROLE: str = 'co_role'
            DIRECTION: str = 'direction'
            DOMAIN_REGION: str = 'domain_region'
            DOMAIN_TOPIC: str = 'domain_topic'
            EXEMPLIFIES: str = 'exemplifies'
            ENTAILS: str = 'entails'
            EQ_SYNONYM: str = 'eq_synonym'
            HAS_DOMAIN_REGION: str = 'has_domain_region'
            HAS_DOMAIN_TOPIC: str = 'has_domain_topic'
            IS_EXEMPLIFIED_BY: str = 'is_exemplified_by'
            HOLO_LOCATION: str = 'holo_location'
            HOLO_MEMBER: str = 'holo_member'
            HOLO_PART: str = 'holo_part'
            HOLO_PORTION: str = 'holo_portion'
            HOLO_SUBSTANCE: str = 'holo_substance'
            HOLONYM: str = 'holonym'
            HYPERNYM: str = 'hypernym'
            HYPONYM: str = 'hyponym'
            IN_MANNER: str = 'in_manner'
            INSTANCE_HYPERNYM: str = 'instance_hypernym'
            INSTANCE_HYPONYM: str = 'instance_hyponym'
            INSTRUMENT: str = 'instrument'
            INVOLVED: str = 'involved'
            INVOLVED_AGENT: str = 'involved_agent'
            INVOLVED_DIRECTION: str = 'involved_direction'
            INVOLVED_INSTRUMENT: str = 'involved_instrument'
            INVOLVED_LOCATION: str = 'involved_location'
            INVOLVED_PATIENT: str = 'involved_patient'
            INVOLVED_RESULT: str = 'involved_result'
            INVOLVED_SOURCE_DIRECTION: str = 'involved_source_direction'
            INVOLVED_TARGET_DIRECTION: str = 'involved_target_direction'
            IS_CAUSED_BY: str = 'is_caused_by'
            IS_ENTAILED_BY: str = 'is_entailed_by'
            LOCATION: str = 'location'
            MANNER_OF: str = 'manner_of'
            MERO_LOCATION: str = 'mero_location'
            MERO_MEMBER: str = 'mero_member'
            MERO_PART: str = 'mero_part'
            MERO_PORTION: str = 'mero_portion'
            MERO_SUBSTANCE: str = 'mero_substance'
            MERONYM: str = 'meronym'
            SIMILAR: str = 'similar'
            OTHER: str = 'other'
            PATIENT: str = 'patient'
            RESTRICTED_BY: str = 'restricted_by'
            RESTRICTS: str = 'restricts'
            RESULT: str = 'result'
            ROLE: str = 'role'
            SOURCE_DIRECTION: str = 'source_direction'
            STATE_OF: str = 'state_of'
            TARGET_DIRECTION: str = 'target_direction'
            SUBEVENT: str = 'subevent'
            IS_SUBEVENT_OF: str = 'is_subevent_of'
            ANTONYM: str = 'antonym'

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
            # Type.ALSO: Type.ALSO,
            Type.ATTRIBUTE: Type.ATTRIBUTE,
            Type.CO_ROLE: Type.CO_ROLE
        }

        def __init__(self, target, relation_type) -> None:
            self.target: str = target
            self.resolved_target: Optional[Synset] = None
            self.relation_type: str = relation_type

        def __str__(self) -> str:
            return f'-{self.relation_type}-> {self.target}'

        def __repr__(self) -> str:
            return f'{self.relation_type}: {self.target}'

        def __getstate__(self) -> dict[str, Any]:
            state = self.__dict__.copy()
            if 'resolved_target' in state:
                del state['resolved_target']  # exclude from being pickled
            return state

        def __setstate__(self, state) -> None:
            self.__dict__.update(state)
            self.resolved_target = None  # restore o a default or None value


ignored_symmetric_synset_relations: Set[Synset.Relation.Type] = {
    Synset.Relation.Type.HYPONYM,
    Synset.Relation.Type.INSTANCE_HYPONYM,
    Synset.Relation.Type.HOLONYM,
    Synset.Relation.Type.HOLO_LOCATION,
    Synset.Relation.Type.HOLO_MEMBER,
    Synset.Relation.Type.HOLO_PART,
    Synset.Relation.Type.HOLO_PORTION,
    Synset.Relation.Type.HOLO_SUBSTANCE,
    Synset.Relation.Type.STATE_OF,
    Synset.Relation.Type.IS_CAUSED_BY,
    Synset.Relation.Type.IS_SUBEVENT_OF,
    Synset.Relation.Type.IN_MANNER,
    Synset.Relation.Type.RESTRICTED_BY,
    Synset.Relation.Type.CLASSIFIED_BY,
    Synset.Relation.Type.IS_ENTAILED_BY,
    Synset.Relation.Type.HAS_DOMAIN_REGION,
    Synset.Relation.Type.HAS_DOMAIN_TOPIC,
    Synset.Relation.Type.IS_EXEMPLIFIED_BY,
    Synset.Relation.Type.INVOLVED,
    Synset.Relation.Type.INVOLVED_AGENT,
    Synset.Relation.Type.INVOLVED_PATIENT,
    Synset.Relation.Type.INVOLVED_RESULT,
    Synset.Relation.Type.INVOLVED_INSTRUMENT,
    Synset.Relation.Type.INVOLVED_LOCATION,
    Synset.Relation.Type.INVOLVED_DIRECTION,
    Synset.Relation.Type.INVOLVED_TARGET_DIRECTION,
    Synset.Relation.Type.INVOLVED_SOURCE_DIRECTION,
    Synset.Relation.Type.CO_PATIENT_AGENT,
    Synset.Relation.Type.CO_INSTRUMENT_AGENT,
    Synset.Relation.Type.CO_RESULT_AGENT,
    Synset.Relation.Type.CO_INSTRUMENT_PATIENT,
    Synset.Relation.Type.CO_INSTRUMENT_RESULT
}

ignored_symmetric_sense_relations: Set[Sense.Relation.Type] = {
    Sense.Relation.Type.HAS_DOMAIN_REGION,
    Sense.Relation.Type.HAS_DOMAIN_TOPIC,
    Sense.Relation.Type.IS_EXEMPLIFIED_BY
}


class Pronunciation:
    """ Pronunciation of a lemma"""

    def __init__(self, value, variety=None) -> None:
        self.value: str = value
        self.variety: Optional[str] = variety


class Example:
    """ Sourced example """

    def __init__(self, text, source=None) -> None:
        self.text: str = text
        self.source: Optional[str] = source


class VerbFrame:
    """ Verb frame """

    def __init__(self, fid, verbframe) -> None:
        self.id: str = fid
        self.verbframe: str = verbframe


class PartOfSpeech(Enum):
    """ Parts of speech """

    NOUN: str = 'n'
    VERB: str = 'v'
    ADJECTIVE: str = 'a'
    ADVERB: str = 'r'
    ADJECTIVE_SATELLITE: str = 's'


class WordnetModel:
    """
    The Model/Lexicon contains all the synsets and entries
    """

    def __init__(self, lexicon_id, label, language, email, wnlicense, version, url) -> None:

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

    def __str__(self) -> str:
        return f"Wordnet '{self.id}'"

    def info(self) -> str:
        """ Counts """
        return f'{self} has {len(self.entries)} entries, {len(self.synsets)} synsets and {sum(1 for _ in self.senses)} senses'

    def info_relations(self) -> str:
        """ Counts of relations """
        return f'{self} has {sum(1 for _ in self.sense_relations)} sense relations and {sum(1 for _ in self.synset_relations)} synset relations'

    @property
    def entry_resolver(self) -> Dict[Tuple[str, str, str | None], Entry]:
        return {e.key: e for e in self.entries}

    @property
    def senses(self) -> Generator[Sense, None, None]:
        """ Senses generator """
        for e in self.entries:
            for s in e.senses:
                yield s

    @property
    def sense_relations(self) -> Generator[Sense.Relation, None, None]:
        """ Sense relations generator """
        for s in self.senses:
            for r in s.relations:
                yield r

    @property
    def synset_relations(self) -> Generator[Synset.Relation, None, None]:
        """ Synset relations generator """
        for ss in self.synsets:
            for r in ss.relations:
                yield r

    @property
    def verbframe_resolver(self) -> Dict[str, str]:
        """ Verb frame resolver factory from id """
        return {f.id: f.verbframe for f in self.verbframes}

    def extend(self) -> None:
        """
        Extend to include inverse relations can be added here
        """
        for ss in self.synsets:
            self.extend_synset_relations(ss)
        for s in self.senses:
            self.extend_sense_relations(s)

    def extend_sense_relations(self, sense: Sense) -> None:
        """
        Add inverse sense relations as needed
        :param sense: sense to extend
        """
        for r in sense.relations:
            if not r.other_type:
                t = Sense.Relation.Type(r.relation_type)
                if t in Sense.Relation.inverses:
                    inv_t = Sense.Relation.inverses[t]
                    if inv_t != t and t not in ignored_symmetric_sense_relations:
                        target_sense = self.sense_resolver[r.target]
                        if not target_sense:
                            raise ValueError(f'Unresolved target {r.target} in relation of type {t} in sense {sense.id}')
                        if not any(r2 for r2 in target_sense.relations if
                                   r2.target == sense.id and not r2.other_type and Sense.Relation.Type(r2.relation_type) == inv_t):
                            target_sense.relations.append(Sense.Relation(sense.id, inv_t.value))

    def extend_synset_relations(self, synset: Synset) -> None:
        """
        Add inverse synset relations as needed
        :param synset: synset to extend
        """
        for r in synset.relations:
            t = Synset.Relation.Type(r.relation_type)
            if t in Synset.Relation.inverses:
                inv_t = Synset.Relation.inverses[t]
                if inv_t != t and t not in ignored_symmetric_synset_relations:
                    target_synset = self.synset_resolver[r.target]
                    if not target_synset:
                        raise ValueError(f'Unresolved target {r.target} in relation of type {t} in synset {synset.id}')
                    if not any(r2 for r2 in target_synset.relations if r2.target == synset.id and Synset.Relation.Type(r2.relation_type) == inv_t):
                        target_synset.relations.append(Synset.Relation(synset.id, inv_t.value))

    def resolve(self) -> None:
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

    def stale(self) -> None:
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
