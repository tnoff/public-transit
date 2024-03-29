#!/usr/bin/env python

import setuptools

setuptools.setup(
    name='public-transit',
    description='Public Transit CLI',
    author='Tyler D. North',
    author_email='ty_north@yahoo.com',
    install_requires=[
        'beautifulsoup4 >= 4.7.1',
        'click==8.0.3',
        'httpretty >= 0.9.6',
        'jsonschema >= 3.0.1',
        'prettytable >= 0.7.2',
        'pytz >= 2018.9',
        'requests >= 2.21.0',
        'SQLAlchemy >= 1.3.1',
    ],
    entry_points={
        'console_scripts' : [
            'bart = transit.cli.bart:main',
            'nextbus = transit.cli.nextbus:main',
            'actransit = transit.cli.actransit:main',
            'trip-planner = trip_planner.cli.planner_script:main',
        ]
    },
    packages=setuptools.find_packages(exclude=["*tests"]),
    version='1.4.0',
)