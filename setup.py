#!/usr/bin/env python
# -*- coding: utf-8 -*-

from codecs import open
from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as readme_file:
    readme = readme_file.read()

with open(path.join(here, 'HISTORY.rst'), encoding='utf-8') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

requirements = [
    'requests>=2.0',
    'netaddr',
    'click',
    'PyYAML'
]

setup(
    name='ipamcli',
    version='0.0.1',
    description='Console client for NOC IPAM module.',
    long_description=readme + '\n\n' + history,
    author='Vadim Aleksandrov',
    author_email='valeksandrov@me.com',
    url='https://github.com/verdel/ipamcli',
    packages=find_packages(),
        entry_points={'console_scripts': ['ipamcli=ipamcli.cli:cli', ], },
    include_package_data=True,
    install_requires=requirements,
    keywords='ipamcli',
    license="MIT",
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'
    ]
)
