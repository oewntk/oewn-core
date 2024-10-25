#  Copyright (c) 2024.
#  Creative Commons 4 for original code
#  GPL3 for rewrite

from setuptools import setup, find_packages

setup(
    name='oewn-core',
    version='1.0',
    author='Bernard Bou, John McCrae',
    author_email='oewntk@gmail.com',
    description='Core library for oewn',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/oewntk/oewn-core',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GPL3 License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        'PyYAML',
    ],
    extras_require={
        'dev': [
            'unittest',
        ],
    },
)