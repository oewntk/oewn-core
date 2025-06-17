#WordNet-LMF 1.3
#===

This migrates [WN-LMF 1.3 (DTD)](https://github.com/globalwordnet/schemas/blob/release-1.3/WN-LMF-1.3.dtd) to XSD form:


This is to equip WordNet with state-of-the-art validation schemas the way FrameNet did.
This move is dictated by the following: DTD does not provide fine-grained control the way XSD does.
The most significant difference between DTDs and XML Schema is the capability to create and use **datatypes**.
XSD schemas define datatypes for elements and attributes while DTD doesn't support them.
This allows for control on what sort of data (ids, content) is expected.
Leveraging datatypes gets errors to bubble up that would otherwise go unnoticed.

### name spaces

Namespaces are left unchanged. Beyond the current namespace, the only namespace is dc:.

### modules

The design is modular:

***dc.xsd*** for dc: namespace.
***idtypes.xsd*** for core id types (it defines ID policy).
***wordtypes.xsd*** for word types (it defines word form policy).
***types.xsd*** for core data types.
***pwn.xsd*** for PWN types.
***ili.xsd*** for ili types.
***meta.xsd*** for meta types.
***core-1.3.xsd*** for elements and the core structure.

This allows for different levels of validation to be performed.

This makes it possible to bring stricter constraints to bear on the same data.
But it does not mean the previous level is incompatible with the next.
For example the data that satisfies WN-LMF-1.3-strict.xsd is a subset of data validated by WN-LMF-1.3.xsd
(or WN-LMF-1.3 is a superset of WN-LMF-1.3).

#### variants

WN-LMF-1.3.xsd
WN-LMF-1.3-strict.xsd which imposes constraints on word characters (it collects the characters that are known to be used,
any new one will raise a validation error)

### OEWN compatibility with 1.3 schema

The current merged file satisfies both:

- WN-LMF-1.3.xsd
- WN-LMF-1.3-strict.xsd

### Validation tool

[Preferred validation tool](https://github.com/1313ou/ewn-validate2) (based on Saxon, fast and efficient)
[Basic validation tool](https://github.com/1313ou/ewn-validate) (based on standard validation tools that come with Java8, may be
slow) 

### Variant

Allows *collocation* relation.

