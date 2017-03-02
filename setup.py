"""
Setup file for Race Data
"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='racedata',
    version='0.1rc1',
    description='Race Data 0.1 Release Candidate 1',
    long_description=long_description,
    url='https://github.com/SenorPez/project-cars-race-data',
    author='Senor Pez',
    author_email='contact_at_github@example.org',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='gaming racing video data streaming',
    packages=find_packages(exclude=['assets', 'tests', 'utils']),
    install_requires=['natsort', 'tqdm'],
)

