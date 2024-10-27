#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite
import os
import sys

from oewn_core import deserialize
from typing import List, Generator

from wordnet import WordnetModel, Sense

data_home = os.environ['OEWN_HOME']
print(f'data={data_home}', file=sys.stderr)
wn: WordnetModel = deserialize.load_pickle(data_home)
sorted_entries: list = sorted(list(wn.entries), key=lambda e: e.lemma)
senses: Generator[Sense, None, None] = wn.senses
sorted_senses: List[Sense] = sorted(list(wn.senses), key=lambda s: s.id)
