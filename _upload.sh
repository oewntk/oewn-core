
#
# Copyright (c) 2024.
# Creative Commons 4 for original code
# GPL3 for rewrite
#

# https://pypi.org/

.venv/bin/python3 -m pip install --upgrade twine
.venv/bin/python3 -m twine upload --repository testpypi dist/*
