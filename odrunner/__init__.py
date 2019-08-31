#
# MIT License
#
# Copyright (c) 2019 Keisuke Sehara
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import datetime as _dt
import uuid as _uuid

VERSION_STR = "1.0a1"

DEFAULT_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

class LogEntry:
    """
    the base model for log entry.

    available 'public' fields must be set by the '_fields' attribute
    of the class.

    the implementation of the setter can be custamized by overriding
    the `set_field` method.

    to change the display behavior of the object, override the
    `display_field` method.
    """

    _fields = ('timestamp', 'category', 'description')

    @staticmethod
    def parse_time(time, format=DEFAULT_DATETIME_FORMAT):
        return _dt.datetime.strptime(str(time), format)

    def __init__(self, timestamp=None, category=None, description=None):
        self.uuid        = _uuid.uuid1()
        self.timestamp   = _dt.datetime.now() if timestamp is None else LogEntry.parse_time(timestamp)
        self.category    = "Comment" if category is None else category
        self.description = '' if description is None else description

    def __getattr__(self, name):
        if name in self.__class__._fields:
            return getattr(self, '_'+name)
        else:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        if (name == 'uuid') or (name.startswith('_')):
            super().__setattr__(name, value)
        elif name in self.__class__._fields:
            self.set_field(name, value)
        else:
            raise AttributeError(f"not settable: {name}")

    def set_field(self, name, value):
        setattr(self, '_'+name, value)

    def display_field(self, name):
        if isinstance(name, int) and (name < len(self.__class__._fields)):
            name = self.__class__._fields[name]
        elif name not in self.__class__._fields:
            raise AttributeError(f"unknown field name: {name}")
        value = getattr(self, '_'+name)
        if name == 'timestamp':
            return value.strftime(DEFAULT_DATETIME_FORMAT)
        else:
            return value

from .subject import Logger as SubjectLogger
from .subject import View   as SubjectView
from .subject import Entry  as SubjectEntry
