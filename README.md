<p align="center">
<img width="256" src="images/oewntk.png" alt="OEWNTK">
</p>

# Open English Wordnet core Python toolkit

This project's purpose is to provide basic load/save utilities in Python for Open English Wordnet models.

The starting point is a number of Python scripts written by JohnMcCrae that used to come with OEWN source.
These have been reworked.

## Dataflows

![Dataflow](images/dataflow.png  "Dataflow")
* 
* YAML -> model
* model -> YAML
* pickle -> model
* model -> pickle
* XML -> model
* model -> XML

## Bare-Bones, No-Frills

Unused code has been trimmed.

In the model, **IDs are not transformed** — there is no mangling to make them valid XML IDs:

* sense IDs are the **sensekey**s,
* synset IDs are the **synsetid**s,
* entries have no ID — they use **(lemma, pos, discriminant)** for resolution
  where _discriminant_ is the possible _indexing_ appended to the part-of-speech, for example:
  (bass,a,None)
  (bass,n,1)
  (bass,n,2)

One-field classes have been replaced with this field.

No processing nor editing of model is performed: it's up to other tools to do it.

No validation of model is performed within core: it's up to other tools to do it. 
There is however and independent _validation_ module (see below) that can be run.

If anything goes wrong, the language and libraries will raise their own exceptions.
However, some exceptions are raised when a requested operation can't carry on.

It is not considered inherent to the model to be exported to XML.
So the model is **XML-agnostic**. XML legacy has been ditched except when it comes to XML exporting / importing in the dedicated
reader and writer.

## Modular

Design is modular: modules do not depend on each other except on _model_. So modules are encapsulated. Chains however
use a supplier and a consumer.

## Typed

Variables are typed to make the code readable and document it.

## No-deps

No deps but YAML (pip install PyYAML)

## Late resolution

Internal cross-dependencies are resolved at a later stage. If resolution is not necessary, this stage may be ignored. This
involves

- the resolution of synsetids in senses to synsets
- the resolution of members in synsets to entries
- the resolution of targets in relations to senses or synsets

The resolved entities are stored as **resolved_*** class members in the object.

## Late extension

Optional extension of relation sets with the addition of inverse relations (if inversable) is possible at a later stage, if
needed.

## Packages

Code comes in 3 packages:

* [oewn_core](oewn_core) which contains model and YAML I/O and knows nothing of oewn_xml
* [oewn_xml](oewn_xml) optional package which contains XML I/O and depends on oewn_core
* [oewn_validate](oewn_validate) optional package which contains model validation and depends on oewn_core, but not on oewn_wml
  since it does not validate XML but only the model's semantics.

## Modules ##

**Model**

- [model](oewn_core/wordnet.py) : Model

**Suppliers**:  YAML/XML/pickle

- [fromyaml](oewn_core/wordnet_fromyaml.py) : Supply model from YAML
- [fromxml](oewn_xml/wordnet_fromxml.py) : Supply model from (one-file) XML

**Consumers**: YAML/XML/pickle

- [toyaml](oewn_core/wordnet_toyaml.py) : Consume model to YAML
- [toxml](oewn_xml/wordnet_toxml.py) : Consume model to (one-file) XML

**Supplier-consumer chains**: YAML2YAML, YAML2XML, XML2YAML

- [yaml_to_yaml](oewn_core/yaml_to_yaml.py) : Chain from YAML supplier to YAML consumer (side effect is normalization)
- [yaml_to_xml](oewn_xml/yaml_to_xml.py)  : Chain from YAML supplier to XML consumer (conversion from XML)
- [xml_to_yaml](oewn_xml/xml_to_yaml.py)  : Chain from XML supplier to YAML consumer (conversion to YAML)

## XML extensions ##

While still conforming to [WN-LMF-1.1.dtd](https://github.com/globalwordnet/schemas/blob/master/WN-LMF-1.1.dtd),

* **wikidata** in synsets is exported in the _dc:subject_ attribute
* **sent** in synsets is exported as \<Example>
* **dc:date** in \<Lexicon> receives the date of XML generation
* **dc:identifier** in \<Lexicon> receives a UID (and is thus unique)

## Sample code ##

**How to load a model:**
```
def main() -> None:
    def get_model() -> WordnetModel:
        if args.pickle:
            from oewn_core.deserialize import load
            return load(args.in_dir, file=args.pickled, resolve=True)
        else:
            from oewn_core.wordnet_fromyaml import load
            return load(args.in_dir, resolve=True)

    arg_parser = argparse.ArgumentParser(description="browse")
    arg_parser.add_argument('--pickle', action='store_true', default='True', help='model to use')
    arg_parser.add_argument('in_dir', type=str, help='from-dir for yaml/pickle')
    arg_parser.add_argument('pickled', type=str, nargs='?', default='oewn.pickle', help='from-pickle')
    args = arg_parser.parse_args()

    wn = get_model()
    browse(wn)
```
Note that loading uses the _resolve=True_ parameter so that reference resolution is done once and for all, 
at an early stage, and _resolved_*_ fields can be used, saving you the trouble of having to look up for ID reference.

**How to browse**:
```
def browse(wn: WordnetModel) -> None:
    entity_resolver = wn.entry_resolver
    e = entity_resolver[('force', 'n', None)]
    print(f'{e}')
    for s in e.senses:
        ss = s.resolved_synset
        print(f'\t{s} -> {ss.members} {ss.definitions}')
        for ssr in ss.relations:
            print(f'\t\t{ssr} {ssr.resolved_target.members} {ssr.resolved_target.definitions}')
        for sr in s.relations:
            print(f'\t\t{sr} {sr.resolved_target}')
```
Note that entry_resolver creates an entry resolver that does not come with the model. 
It is advisable to save it in a variable for later use to avoid recreating this dictionary every time a lookup is initiated.

## Testing ##

* yaml → model → yaml
* yaml → model → xml → model → yaml
* yaml → pickle → yaml

must produce identical input and output at the ends of the chains

XML single output file must validate against [WN-LMF-1.1.dtd](https://github.com/globalwordnet/schemas/blob/master/WN-LMF-1.3.dtd)

The _validate_ package tests the model's coherence (but does not test XML well-formedness).

## Authorship ##

Original code was written by John McCrae <john@mccr.ae>
Bernard Bou revised, trimmed, revamped it <1313ou@gmail>.

## Licence ##

Licence is CC-4 for original code.

License is GPL-3 for revisions.

## Related ##

The [oewntk project](https://github.com/oewntk/oewntk) is a tool suite written in Kotlin for JVM,
that has similar design principles. Most notably, it exports to SQL, WNDB and JSON formats.