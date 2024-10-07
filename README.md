<p align="center">
<img width="256" src="images/oewntk.png" alt="OEWNTK">
</p>

# Open English Wordnet core Python toolkit

This project's purpose is to provide basic load/save utilities in Python for Open English Wordnet models. 

The starting point is a number of Python scripts written by JohnMcCrae that used to come with OEWN source.
These have been reworked.

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
So the model is XML-agnostic. XML legacy has been ditched except when it comes to XML exporting / importing in the dedicated reader and writer.

## Modular

Design is modular: modules do not depend on each other except model. Chains however
use a supplier and a consumer.

## Typed

Variables are typed to make the code readable and document it.

## No-deps

No deps but YAML (pip install PyYAML)

## Late resolution

Internal cross-dependencies are resolved at a later stage. If resolution is not necessary, this stage may be ignored. This involves 
- the resolution of synsetids in senses to synsets
- the resolution of members in synsets to entries
- the resolution of targets in relations to senses or synsets

The resolved entities are stored as **resolved_*** class members in the object.

## Late extension

Optional extension of relation sets with the addition of inverse relations (if inversable) is possible at a later stage, if needed.


## Modules ##

**Model**

- [model](wordnet.py) : Model

**Suppliers**:  YAML/XML/pickle

- [fromyaml](wordnet_fromyaml.py) : Supply model from YAML

**Consumers**: YAML/XML/pickle

- [toyaml](wordnet_toyaml.py) : Consume model to YAML

**Supplier-consumer chains**: YAML2YAML

- [yaml_to_yaml](yaml_to_yaml.py) : Chain from YAML supplier to YAML consumer (side effect is normalization)

## Authorship ##

Original code was written by John McCrae <john@mccr.ae>
Bernard Bou revised, trimmed, revamped it <1313ou@gmail>.
Licence is CC-4 for original code.
License is GPL-3 for revisions.