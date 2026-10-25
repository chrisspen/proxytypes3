#!/usr/bin/env python
from os import path
from setuptools import setup, find_packages

import proxytypes3

with open(path.join(path.abspath(path.dirname(__file__)), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='proxytypes3',
    version=proxytypes3.__version__,
    description="General purpose proxy and wrapper types.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/chrisspen/ProxyTypes3",
    author="Chris Spencer",
    author_email="chrisspen@gmail.com",
    license="MIT",
    #https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 6 - Mature',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12'
    ],
    test_suite='tests',
    packages=find_packages(),
    zip_safe=False
)
