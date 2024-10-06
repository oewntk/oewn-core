<p align="center">
<img width="256" src="images/oewntk.png" alt="OEWNTK">
</p>

# Open English Wordnet core Python toolkit

This project will group all toolkit repos that will provide suppliers and consumers of Open English Wordnet models.

## Dataflow

![Dataflow](images/dataflow.png  "Dataflow")

## Bare-Bones, No-Frills

Unused code has been trimmed.

One-field classes have been replaced with this field.

No processing nor editing of model is performed: it's up to other tools to do it.
No validation of model is performed: it's up to other tools to do it.

If something goes wrong, the language and libraries will raise their own exceptions. 
However, some exceptions are raised when a requested operation can't carry on.

It is not considered inherent to the model to be exported to XML. 
So the model is XML-agnostic.

## Modular

Design is modular: modules do not depend on each other except model. Chains however
use a supplier and a consumer.

## Typed

Variables are typed to make the code readable and document it.

## No-deps

No deps but YAML (pip install PyYAML)

## Late resolution

Internal dependencies are resolved at a later stage. If resolution is not necessary, this stage may be ignored. Tthis involves 
- the resolution of sense synsetid to synset
- the resolution of synset members to entries
- the resolution of relation targets to senses or synsets
The resolved entity is stored as a resolved_* class field

## Late extension

Optional extension of relation sets with the addition of inverse relations (if inversable) is possible at a later stage, if needed.


## Modules ##

**Model**

- [model](wordnet.py) : Model

**Suppliers**:  YAML/XML/pickle

- [fromyaml](wordnet_fromyaml) : Supply model from YAML

**Consumers**: YAML/XML/pickle

- [toyaml](wordnet_toyaml) : Consume model to YAML

**Supplier-consumer chains**: YAML2YAML, YAML2XML, XML2YAML

- [yaml_to_yaml](wml_to_yaml.py) : Chain from YAML supplier to YAML consumer (side effect is normalization)

## Authorship ##

Original code was written by John McCrae.
Bernard Bou revised, trimmed, revamped it.
Licence is CC-4 for original code.
License is GPL-3 for revisions.