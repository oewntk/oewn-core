"""
WordNet from-XML utilities
Uses a SAX parser

Author: John McCrae <john@mccr.ae> for original code
Author: Bernard Bou <1313ou@gmail.com> for rewrite and revamp
"""

#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import argparse
import codecs
import re
import sys
import time
from xml.sax import ContentHandler, parse

from wordnet import *
import wordnet_xml as xml


def make_synset_id(xml_synsetid):
    return xml.from_xml_synset_id(xml_synsetid)


def make_sense_id(xml_senseid):
    return xml.from_xml_sense_id(xml_senseid)


def make_member(xml_member, entry_resolver):
    e = entry_resolver[xml_member]
    return e.lemma


def make_members(xml_members, entry_resolver):
    return [make_member(m, entry_resolver) for m in xml_members.split(' ')]


class SAXParser(ContentHandler):
    """
    SAX parser
    """

    def __init__(self):
        ContentHandler.__init__(self)

        # local data
        self.lexicon: Optional[WordnetModel] = None
        self.entry: Optional[Entry] = None
        self.sense: Optional[Sense] = None
        self.synset: Optional[Synset] = None
        self.defn: Optional[str] = None
        self.ili_defn: Optional[str] = None
        self.example: Optional[str] = None
        self.example_source: Optional[str] = None
        self.usage: Optional[str] = None
        self.pronunciation: Optional[str] = None
        self.pronunciation_variety: Optional[str] = None

        # top accumulators
        self.entries: List[Entry] = []
        self.synsets: List[Synset] = []
        self.verbframes: List[VerbFrame] = []
        # resolvers
        self.sense_resolver: Dict[str, Sense] = {}
        self.synset_resolver: Dict[str, Synset] = {}
        self.member_resolver: Dict[Tuple[str, str], Entry] = {}
        self.entry_resolver: Dict[str, Entry] = {}

    discriminant_pattern = r'\-\d+$'

    def startElement(self, name, attrs):
        if name == 'LexicalEntry':
            entryid = attrs.get('id')
            match = re.search(self.discriminant_pattern, entryid)
            d = match.group()[1:] if match else None
            self.entry = Entry(None, None, d)
            if entryid in self.entry_resolver:
                raise ValueError(f'Duplicate entry ID while parsing: {entryid}')
            self.entry_resolver[entryid] = self.entry
        elif name == 'Sense':
            senseid = xml.from_xml_sense_id(attrs['id'])
            synsetid = make_synset_id(attrs['synset'])
            verbframes = attrs['subcat'].split(' ') if 'subcat' in attrs else None
            self.sense = Sense(senseid, self.entry, synsetid, attrs.get('adjposition'))
            self.sense.verbframeids = verbframes
        elif name == 'Synset':
            synsetid = make_synset_id(attrs['id'])
            members = make_members(attrs.get('members', ''), self.entry_resolver)
            pos = PartOfSpeech(attrs['partOfSpeech']).value
            self.synset = Synset(synsetid, pos, members, attrs.get('lexfile'))
            self.synset.ili = attrs['ili']
            self.synset.wikidata = attrs.get('dc:subject')
            self.synset.source = attrs.get('dc:source')
        elif name == 'Lemma':
            self.entry.lemma = attrs['writtenForm']
            self.entry.pos = attrs['partOfSpeech']
        elif name == 'Form':
            self.entry.forms.append(attrs['writtenForm'])
        elif name == 'Definition':
            self.defn = ''
        elif name == 'ILIDefinition':
            self.ili_defn = ''
        elif name == 'Example':
            self.example = ''
            self.example_source = attrs.get('dc:source')
        elif name == 'Usage':
            self.example = ''
        elif name == 'SynsetRelation':
            target = make_synset_id(attrs['target'])
            rtype = attrs['relType']
            self.synset.relations.append(Synset.Relation(target, Synset.Relation.Type(rtype).value))
        elif name == 'SenseRelation':
            target = make_sense_id(attrs['target'])
            rtype = attrs['relType']
            is_other = rtype == Sense.Relation.Type.OTHER.value
            rtype2 = Sense.Relation.OtherType(attrs['dc:type']).value if is_other else Sense.Relation.Type(rtype).value
            self.sense.relations.append(Sense.Relation(target, rtype2, is_other))
        elif name == 'SyntacticBehaviour':
            self.verbframes.append(VerbFrame(attrs['id'], attrs['subcategorizationFrame']))
        elif name == 'Pronunciation':
            self.pronunciation = ''
            self.pronunciation_variety = attrs.get('variety')
        elif name == 'Lexicon':
            self.lexicon = WordnetModel(
                attrs['id'],
                attrs['label'],
                attrs['language'],
                attrs['email'],
                attrs['license'],
                attrs['version'],
                attrs['url'])
        elif name == 'LexicalResource':
            pass
        else:
            raise ValueError(f'Unexpected Tag: {name}')

    def endElement(self, name):
        if name == 'LexicalEntry':
            self.entries.append(self.entry)
            self.entry = None
        elif name == 'Sense':
            self.entry.senses.append(self.sense)
            if self.sense.id in self.sense_resolver:
                raise ValueError(f'Duplicate sense ID while parsing: {self.sense.id}')
            self.sense_resolver[self.sense.id] = self.sense
            mk = (self.entry.lemma, self.sense.synsetid)
            if mk in self.member_resolver:
                raise ValueError(f'Duplicate member ID while parsing: {mk}')
            self.member_resolver[mk] = self.entry
            self.sense = None
        elif name == 'Synset':
            self.synsets.append(self.synset)
            if self.synset.id in self.member_resolver:
                raise ValueError(f'Duplicate synset ID while parsing: {self.synset.id}')
            self.synset_resolver[self.synset.id] = self.synset
            self.synset = None
        elif name == 'Definition':
            self.synset.definitions.append(self.defn)
            self.defn = None
        elif name == 'ILIDefinition':
            self.synset.ili_definitions(self.ili_defn)
            self.ili_defn = None
        elif name == 'Example':
            if self.synset:
                e = Example(self.example, self.example_source) if self.example_source else self.example
                self.synset.examples.append(e)
            elif self.sense:
                self.sense.examples.append(self.example)
            self.example = None
        elif name == 'Usage':
            self.synset.usages.append(self.usage)
            self.usage = None
        elif name == 'Pronunciation':
            self.entry.pronunciations.append(Pronunciation(self.pronunciation, self.pronunciation_variety))
            self.pronunciation = None

    def characters(self, content):
        if self.defn is not None:
            self.defn += content
        elif self.ili_defn is not None:
            self.ili_defn += content
        elif self.example is not None:
            self.example += content
        elif self.usage is not None:
            self.usage += content
        elif self.pronunciation is not None:
            self.pronunciation += content
        elif content.strip() == '':
            pass
        else:
            raise ValueError(f'Text content not expected: "{content}"')

    def get_parsed(self):
        wn = self.lexicon
        wn.entries = self.entries
        wn.synsets = self.synsets
        wn.verbframes = self.verbframes
        wn.sense_resolver = self.sense_resolver
        wn.synset_resolver = self.synset_resolver
        wn.member_resolver = self.member_resolver
        return wn


def load(wordnet_file):
    with codecs.open(wordnet_file, encoding='utf-8') as source:
        sax_parser = SAXParser()
        parse(source, sax_parser)
        return sax_parser.get_parsed()


def main():
    arg_parser = argparse.ArgumentParser(description='load from xml')
    arg_parser.add_argument('in_file', type=str, help='from-file')
    args = arg_parser.parse_args()
    wn = load(args.in_file)
    wn.resolve()
    print(wn)
    return wn


if __name__ == '__main__':
    start_time = time.time()
    main()
    end_time = time.time()
    duration = end_time - start_time
    print(f"Loading took {duration:.6f} seconds", file=sys.stderr)
