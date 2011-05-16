#!/usr/bin/env python

import os
from distutils.core import setup

version = '0.4'

classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: BSD License",
    "Programming Language :: Python",
    "Operating System :: OS Independent",
    "Topic :: Software Development :: Libraries",
    "Topic :: Utilities",
    "Environment :: Web Environment",
    "Framework :: Django",
]

root_dir = os.path.dirname(__file__)
if not root_dir:
    root_dir = '.'
long_desc = open(root_dir + '/README.rst').read()

setup(
    name='django-threespot',
    version=version,
    url='http://github.com/mazelife/django-threespot/',
    author='James Stevenson',
    author_email='james.m.stevenson at threespot dot com',
    license='BSD License',
    packages=['threespot'],
    package_dir={'threespot': 'threespot'},
    description=(
        'Various cool, useful utilities and small, reusable django apps'
    ),
    classifiers=classifiers,
    long_description=long_desc,
    install_requires=['django>=1.3']
)
