# -*- coding: utf-8 -*-
"""
    tests.types.test_string
    ~~~~~~~~~~~~~~~~~~~~~~~

    A WSGI compliant REST micro-framework.

    :copyright: (c) 2016 Anomaly Software
    :license: Apache 2.0, see LICENSE for more details.
"""
from prestans3.types import String


def test_can_create_string():
    String()


def test_can_init_string():
    String("init")
