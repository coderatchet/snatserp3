# -*- coding: utf-8 -*-
"""
    setup.py
    ~~~~~~~~
    
    A WSGI compliant REST micro-framework.

    :copyright: (c) 2016 Anomaly Software
    :license: Apache 2.0, see LICENSE for more details.
"""

import os
import shutil

from setuptools import setup, find_packages
from setuptools.command.install import install

from prestans3 import __version__


setup(
    name="prestans3",
    version = __version__,
    description = 'A WSGI compliant REST micro-framework',
    url = 'https://github.com/anomaly/prestans3.git',
    long_description = open("README.rst").read(),
    download_url = 'https://github.com/anomaly/prestans3/archive/' + __version__ + '.tar.gz',
    license = 'Apache 2.0',
    author = 'Anomaly Software',
    author_email = 'support@anomaly.net.au',
    maintainer = 'Anomaly Software',
    maintainer_email = 'support@anomaly.net.au',
    classifiers = [
        'Environment :: Web Environment',
        'License :: OSI Approved',
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    platforms = ['any'],
    packages = find_packages(),
    include_package_data = True,
    install_requires = [],
    tests_require = ['pytest'],
    setup_requires = ['pytest-runner'],
)