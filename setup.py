#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

from setuptools import setup, find_packages

setup(
    name='oewn-core',
    version='1.3.2',
    author='Bernard Bou, John McCrae',
    author_email='oewntk@gmail.com',
    description='Core library for oewn',
    long_description=open('PKG-INFO.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/oewntk/oewn-core',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    license = 'GPL-3.0',
    python_requires='>=3.9',
    install_requires=[
        'PyYAML',
    ],
    extras_require={
        'dev': [
            'unittest',
        ],
    },
)