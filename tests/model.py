"""
WordNet model made available for tests
Author: John McCrae <john@mccr.ae> for original code
Author: Bernard Bou <1313ou@gmail.com> for rewrite and revamp
"""
#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

import os
import sys
from typing import List

from oewn_core.deserialize import load
from oewn_core.wordnet import WordnetModel, Sense, Entry

data_home = os.environ['OEWN_HOME']
print(f'data={data_home}', file=sys.stderr)
wn: WordnetModel = load(data_home, extend=False)

sorted_entries: List[Entry] = sorted(list(wn.entries), key=lambda e: e.lemma)
sorted_senses: List[Sense] = sorted(list(wn.senses), key=lambda s: s.id)
