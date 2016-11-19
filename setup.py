#!/usr/bin/env python

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
doclink = """
Documentation
-------------

The full documentation is at http://helix-python.rtfd.org."""
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='helix-python',
    version='0.1.0',
    description='helix',
    long_description=readme + '\n\n' + doclink + '\n\n' + history,
    author='Eric plaster',
    author_email='eric@insito.me',
    url='https://github.com/xuru/helix-python',
    packages=[
        'helix',
    ],
    package_dir={'helix': 'helix'},
    include_package_data=True,
    install_requires=[
        'pendulum', 'marshmallow', 'requests', 'wheel>=0.22'
    ],
    license='MIT',
    zip_safe=False,
    keywords='helix',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
