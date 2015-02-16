#!/usr/bin/env python

from setuptools import setup

setup(
    name='public-transit',
    description='Public Transit Info',
    author='Tyler D. North',
    author_email='tylernorth18@gmail.com',
    install_requires=[
        'beautifulsoup4>=4.3.2',
        'httpretty>=0.8.4',
        'nose>=1.3.4',
        'requests==2.5.1',
    ],
    scripts=[
    ],
    packages=[
        'transit',
    ],
    version='0.0.8',
)
