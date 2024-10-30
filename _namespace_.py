#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite
import sys
import pprint
from oewn_core import wordnet as core
from oewn_xml import wordnet_xml as xml


def debug_module_namespace(name):
    m = __import__(name)
    print(f"\n=== {m} module attributes ===")
    pprint.pprint(dir(m))


def debug_core_module_namespace():
    print("\n=== core module attributes ===")
    pprint.pprint(dir(core))


def debug_xml_module_namespace():
    print("\n=== xml module attributes ===")
    pprint.pprint(dir(xml))


def debug_current_module_namespace():
    print("=== Local namespace ===")
    pprint.pprint(locals())
    print("\n=== Global namespace ===")
    pprint.pprint(globals())


def debug_current_module_search_path():
    print("\n=== Python module search path ===")
    pprint.pprint(sys.path)


def debug_loaded_modules():
    print("\n=== Currently loaded modules ===")
    pprint.pprint(sys.modules)


def debug_namespace():
    # 1. Print current module's namespace
    debug_current_module_namespace()

    # 2. Check module search path
    debug_current_module_search_path()

    # 3. List loaded modules
    debug_loaded_modules()

    # 4. Inspect specific module attributes
    debug_core_module_namespace()
    debug_xml_module_namespace()

    # 4b. Inspect specific module attributes
    debug_module_namespace("oewn_core.wordnet")
    debug_module_namespace("oewn_xml.wordnet_xml")


if __name__ == "__main__":
    debug_namespace()
