# -*- coding: utf-8 -*-
"""
    prestans.types.string
    ~~~~~~~~~~~~~~~~~~~~~
    
    A WSGI compliant REST micro-framework.

    :copyright: (c) 2016 Anomaly Software
    :license: Apache 2.0, see LICENSE for more details.
"""
import codecs

from prestans3.future import istext
from . import ImmutableType
import re


class DataURLFile(ImmutableType):
    """
    Implements a `Data URI string`_\ . The |DataURLFile| embeds a mime type, encoding and content into a string and is
    supported by HTML, CSS and Javascript for embedded content (e.g. a `png`_).

    .. _Data URI string: http://en.wikipedia.org/wiki/Data_URI_scheme
    .. _png: https://en.wikipedia.org/wiki/Data_URI_scheme#HTML
    """

    regex = re.compile(r'^data:([\w/\-\.]+);(\w+),(.*)$')

    @classmethod
    def generate_filename(cls):
        import uuid
        return uuid.uuid4().hex

    @classmethod
    def from_value(cls, value):
        try:
            return super(DataURLFile, cls).from_value(value)
        except:
            # py2to3 replace istext(value) with isinstance(value, str)
            if not istext(value):
                raise TypeError("{} of type {} is not coercible to type {}".format(value, value.__class__.__name__,
                                                                                   cls.__name__))
            else:
                return DataURLFile(value)

    def __init__(self, encoded_data):
        self._encoded_data = encoded_data
        match = self.regex.match(encoded_data)
        if match:
            # todo match start and end should be 0 and len(encoded_data) respectively else raise error
            [a, b, c] = match.groups()
            self._mime_type = a
            self._encoding = b
            self._contents = c
        else:
            raise ValueError("encoded_data was not in the expected format. for an explaination of how to format a "
                             "data url file, see https://en.wikipedia.org/wiki/Data_URI_scheme")
        super(DataURLFile, self).__init__()

    @property
    def mime_type(self):
        return self._mime_type

    @property
    def encoding(self):
        return self._encoding

    @property
    def contents(self):
        return self._contents

    @property
    def decoded_contents(self):
        return codecs.lookup(self.encoding).decode(self.contents)[0]
