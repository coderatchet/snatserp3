# -*- coding: utf-8 -*-
"""
    prestans.types.string
    ~~~~~~~~~~~~~~~~~~~~~
    
    A WSGI compliant REST micro-framework.

    :copyright: (c) 2016 Anomaly Software
    :license: Apache 2.0, see LICENSE for more details.
"""
from prestans3.errors import ValidationException, PropertyConfigError
from prestans3.utils import is_str

from . import ImmutableType


class String(ImmutableType, str):
    def __init__(self, value=None):
        if value is None:
            value = ""
        str.__init__(value)

    @classmethod
    def from_value(cls, value):
        if not is_str(value):
            raise TypeError(
                "{} of type {} is not coercible to {}".format(value, value.__class__.__name__, cls.__name__))
        return String(value)


def _str_min_length(instance, config):
    length = len(instance)
    if length < config:
        raise ValidationException(instance.__class__,
                                  '{} str_min_length config is {} however len("{}") == {}'.format(
                                      instance.__class__.__name__,
                                      config, instance,
                                      length))


def _str_max_length(instance, config):
    length = len(instance)
    if length > config:
        raise ValidationException(instance.__class__,
                                  '{} str_max_length config is {} however len("{}") == {}'.format(
                                      instance.__class__.__name__,
                                      config, instance,
                                      length))


def _min_max_string_check_config(type, config):
    if config is not None and 'str_min_length' in config and 'str_max_length' in config \
            and config['str_min_length'] > config['str_max_length']:
        raise PropertyConfigError(type, 'str_min_length and str_max_length', 'invalid {} property configuration: ' + \
                                  'str_min_length config of {} is greater than str_max_length config of {}'.format(
                                      type.__name__, config['str_min_length'], config['str_max_length']))


String.register_property_rule(_str_min_length, name="str_min_length")
String.register_property_rule(_str_max_length, name="str_max_length")
String.register_config_check(_min_max_string_check_config, name="min_max_string_check_config")
