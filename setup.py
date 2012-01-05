#!/usr/bin/env python

import os
from distutils.core import setup

version = '0.5'

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

def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
threespot_dir = 'threespot'

for dirpath, dirnames, filenames in os.walk(threespot_dir):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))
    elif filenames:
        data_files.append(
            [dirpath, [os.path.join(dirpath, f) for f in filenames]]
        )

long_desc = open(root_dir + '/README.rst').read()


setup(
    name='django-threespot',
    version=version,
    url='http://github.com/mazelife/django-threespot/',
    author='James Stevenson',
    author_email='james.m.stevenson at threespot dot com',
    license='BSD License',
    data_files=data_files,
    packages=packages,
    package_dir={'threespot': 'threespot'},
    description=(
        'Various cool, useful utilities and small, reusable django apps'
    ),
    classifiers=classifiers,
    long_description=long_desc,
    install_requires=['django>=1.3']
)
