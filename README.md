# docassemble-DADataType

This is a module to give Docassemble the ability to ask datatype-approriate default questions
with regard to individual variables, so that the "generic object" feature can be used with
regard to booleans, numbers, etc.

The use case is for rapid prototyping. If you have an external tool with a data structure and known datatypes,
you can export that datastructure as a set of objects for a docassemble interview, and specify only
your goal (perhaps a document template), and you will have a bare-bones functional interview without
having to draft any question blocks.

## Installation

It can be installed inside your docassemble package manager by providing the address for this github repository.

## Use

Inside your interview, load the module and include the default questions interview file.

```
modules:
  - docassemble.DADataType
---
include:
  - docassemble.DADataType:/data/questions/DADataType.yml
```

Now, create an `objects` block, using the available DADT classes, or load objects from a YAML or JSON file.

The available datatypes are currently:

* DADTNumber
* DADTString
* DADTBoolean
* DADTContinue
* DADTTime
* DADTDate
* DADTDateTime
* DADTEmail