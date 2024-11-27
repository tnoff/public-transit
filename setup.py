#!/usr/bin/env python
import os
import setuptools

THIS_DIR = os.path.dirname(__file__)
REQUIREMENTS_FILES = [os.path.join(THIS_DIR, 'requirements.txt')]
VERSION_FILE = os.path.join(THIS_DIR, 'VERSION')

required = []
for file_name in REQUIREMENTS_FILES:
    # Not sure why but tox seems to miss the file here
    # So add the check
    if os.path.exists(file_name):
        with open(file_name) as f:
            required += f.read().splitlines()

try:
    with open(VERSION_FILE) as r:
        version = r.read().strip()
except FileNotFoundError:
    version = '0.0.1'

setuptools.setup(
    name='public-transit',
    description='Public Transit CLI',
    author='Tyler D. North',
    author_email='me@tyler-north.com',
    install_requires=required,
    entry_points={
        'console_scripts' : [
            'bart = transit.cli.bart:main',
            'nextbus = transit.cli.nextbus:main',
            'actransit = transit.cli.actransit:main',
            'trip-planner = trip_planner.cli.planner_script:main',
        ]
    },
    packages=setuptools.find_packages(exclude=["*tests"]),
    version=version,
)