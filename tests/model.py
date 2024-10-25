#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite
import os
import sys

from core import deserialize

data_home = os.environ['OEWN_HOME']
print(f'data={data_home}', file=sys.stderr)
wn = deserialize.load_pickle(data_home)
sorted_entries = sorted(list(wn.entries), key=lambda e: e.lemma)
senses = wn.senses
sorted_senses = sorted(list(wn.senses), key=lambda s: s.id)
