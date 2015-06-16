#!/usr/bin/env python

import setuptools

setuptools.setup(
    name='public-transit',
    description='Public Transit Info',
    author='Tyler D. North',
    author_email='tylernorth18@gmail.com',
    install_requires=[
        'beautifulsoup4>=4.3.2',
        'httpretty>=0.8.4',
        'nose>=1.3.4',
        'prettytable>=0.7.2',
        'requests==2.5.1',
    ],
    entry_points={
        'console_scripts' : [
            'transit = scripts.transit_tool:main',
        ]
    },
    packages=setuptools.find_packages(),
    version='0.1.1',
)
