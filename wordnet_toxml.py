"""
WordNet to-XML utilities

Author: John McCrae <john@mccr.ae> for original code
Author: Bernard Bou <1313ou@gmail.com> for rewrite and revamp
"""

#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import uuid
from typing import List, Dict, Tuple, Union

import wordnet_xml as wnxml
from datetime import datetime

from wordnet import WordnetModel, Sense, Entry, Synset, Pronunciation, VerbFrame, Example

I = '  '  # indentation


def lexicon_to_xml(wn: WordnetModel, out, comments=None):
    """
    Lexicon to XML
    :param wn: lexicon
    :param out: output XML file
    :param comments: optional comments for relations
    :return: None
    """
    out.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    out.write('<!DOCTYPE LexicalResource SYSTEM "http://globalwordnet.github.io/schemas/WN-LMF-1.1.dtd">\n')
    out.write('<LexicalResource xmlns:dc="https://globalwordnet.github.io/schemas/dc/">\n')
    out.write(f"""{I * 1}<Lexicon id="{wn.id}"
        label="{wn.label}"
        language="{wn.language}"
        email="{wn.email}"
        license="{wn.license}"
        version="{wn.version}"
        url="{wn.url}"
        dc:identifier="{uuid.uuid4()}"
        dc:date="{datetime.now().strftime("%Y-%m-%d %H:%M")}">\n""")
    for entry in sorted(wn.entries, key=lambda e: make_entry_id(e)):  # key=lambda e: e.lemma):
        entry_to_xml(entry, out, comments)
    for synset in sorted(wn.synsets, key=lambda ss: ss.id):
        synset_to_xml(synset, wn.member_resolver, out, comments)
    for verbframe in sorted(wn.verbframes, key=lambda f: f.id):
        verbframe_to_xml(verbframe, out)
    out.write(f'{I * 1}</Lexicon>')
    out.write('</LexicalResource>\n')


def entry_to_xml(entry: Entry, out, comments):
    eid = make_entry_id(entry)
    out.write(f'{I * 2}<LexicalEntry id="{eid}">\n')
    lemma_to_xml(entry.lemma, entry.pos, entry.pronunciations, out)
    for form in entry.forms:
        form_to_xml(form, out)
    for sense in entry.senses:
        sense_to_xml(sense, out, comments)
    out.write(f'{I * 2}</LexicalEntry>\n')


def sense_to_xml(sense: Sense, out, comments):
    a = f' adjposition="{sense.adjposition}"' if sense.adjposition else ''
    c = f' subcat="{' '.join(sense.subcat)}"' if sense.subcat else ''
    n = f' n="sense.n"'
    sid = make_sense_id(sense.id)
    ssid = make_synset_id(sense.synsetid)
    if len(sense.relations) > 0:
        out.write(f'{I * 3}<Sense id="{sid}"{n}{a}{c} synset="{ssid}">\n')
        for rel in sense.relations:
            sense_relation_to_xml(rel, out, comments)
        out.write(f'{I * 3}</Sense>\n')
    else:
        out.write(f'{I * 3}<Sense id="{sid}"{n}{a}{c} synset="{ssid}"/>\n')


def synset_to_xml(synset: Synset, member_resolver: Dict[Tuple[str, str], Entry], out, comments):
    if comments and synset.id in comments:
        out.write(f'{I * 2}<!-- %s -->\n' % comments[synset.id])
    ssid = make_synset_id(synset.id)
    p = synset.pos
    m = ' '.join([make_entry_id_from_member(m, synset.id, member_resolver) for m in synset.members])
    l = synset.lex_name
    i = synset.ili
    s = f' dc:source="{synset.source}"' if synset.source else ''
    out.write(f'{I * 2}<Synset id="{ssid}" ili="{i}" members="{m}" partOfSpeech="{p}" lexfile="{l}"{s}>\n')

    for definition in synset.definitions:
        definition_to_xml(definition, out)
    if synset.ili_definition:
        definition_to_xml(synset.ili_definition, out, True)
    for rel in synset.relations:
        synset_relation_to_xml(rel, out, comments)
    for ex in synset.examples:
        example_to_xml(ex, out)
    for us in synset.usages:
        usage_to_xml(us, out)
    out.write(f'{I * 2}</Synset>\n')


def lemma_to_xml(lemma: str, pos: str, pronunciations: List[Pronunciation], out):
    w = wnxml.escape_xml_lit(lemma)
    p = pos
    if pronunciations:
        out.write(f'{I * 3}<Lemma writtenForm="{w}" partOfSpeech="{p}">\n')
        for pronunciation in pronunciations:
            pronunciation_to_xml(pronunciation, out)
        out.write(f'{I * 3}</Lemma>\n')
    else:
        out.write(f'{I * 3}<Lemma writtenForm="{w}" partOfSpeech="{p}"/>\n')


def pronunciation_to_xml(pronunciation: Pronunciation, out):
    v = f' variety="{pronunciation.variety}"' if pronunciation.variety else ''
    p = wnxml.escape_xml_lit(pronunciation.value)
    out.write(f'{I * 4}<Pronunciation{v}>{p}</Pronunciation>\n')


def form_to_xml(form: str, out):
    f = wnxml.escape_xml_lit(form)
    out.write(f'{I * 4}<Form writtenForm="{f}"/>\n')


def definition_to_xml(definition: str, out, is_ili=False):
    d = wnxml.escape_xml_lit(definition)
    xml = f'{I * 3}<ILIDefinition>{d}</ILIDefinition>\n' if is_ili else f'{I * 3}<Definition>{d}</Definition>\n'
    out.write(xml)


def example_to_xml(example: Union[str, Example], out):
    e = wnxml.escape_xml_lit(example.text if isinstance(example, Example) else example)
    s = example.source if isinstance(example, Example) and example.source else None
    xml = f'{I * 3}<Example dc:source="{wnxml.escape_xml_lit(s)}">{e}</Example>\n' if s else f'{I * 3}<Example>{e}</Example>\n'
    out.write(xml)


def usage_to_xml(usage: str, out):
    u = wnxml.escape_xml_lit(usage)
    out.write(f'{I * 3}<Usage>{u}</Usage>\n')


def synset_relation_to_xml(synset_relation: Synset.Relation, out, comments):
    r = synset_relation.relation_type
    t = make_sense_id(synset_relation.target)
    out.write(f'{I * 3}<SynsetRelation relType="{r}" target="{t}"/>')
    if comments and synset_relation.target in comments:
        out.write(f' <!-- {comments[synset_relation.target]} -->')
    out.write('\n')


def sense_relation_to_xml(sense_relation: Sense.Relation, out, comments):
    t = make_sense_id(sense_relation.target)
    r = sense_relation.relation_type
    o = sense_relation.other_type
    if o:
        out.write(f'{I * 4}<SenseRelation relType="other" target="{t}" dc:type="{r}"/>')
    else:
        out.write(f'{I * 4}<SenseRelation relType="{r}" target="{t}"/>')
    if comments and sense_relation.target in comments:
        out.write(f' <!-- {comments[sense_relation.target]} -->')
    out.write('\n')


def verbframe_to_xml(verbframe: VerbFrame, out):
    fid = verbframe.id
    f = wnxml.escape_xml_lit(verbframe.verbframe)
    out.write(f'{I * 2}<SyntacticBehaviour id="{fid}" subcategorizationFrame="{f}"/>\n')


def make_entry_id(entry):
    return _make_entry_id(entry.lemma, entry.pos, entry.discriminant)


def make_entry_id_from_member(lemma: str, synsetid: str, member_resolver: Dict[Tuple[str, str], Entry]):
    if not member_resolver:
        raise ValueError('Null or empty member resolver')
    k = (lemma, synsetid)
    if k not in member_resolver:
        raise ValueError(f'Member resolver cannot resolve {k}')
    e = member_resolver[k]
    return _make_entry_id(lemma, e.pos, e.discriminant)


def _make_entry_id(lemma: str, pos: str, discriminant: str):
    p = pos
    d = discriminant if discriminant else ''
    return f'{wnxml.key_prefix}{wnxml.escape_lemma(lemma)}-{p}{d}'


def make_synset_id(synsetid: str):
    return f'{wnxml.key_prefix}{synsetid}'


def make_sense_id(senseid: str):
    return wnxml.escape_sensekey(senseid)


def save(wn: WordnetModel, path):
    with open(path, 'w', encoding='utf-8') as out:
        lexicon_to_xml(wn, out)
