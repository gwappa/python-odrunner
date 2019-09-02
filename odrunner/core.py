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

DEBUG = True

DEFAULT_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DEFAULT_DATE_FORMAT     = "%Y-%m-%d"

def debug(msg, end='\n', flush=True):
    if DEBUG == True:
        import sys
        print(msg, file=sys.stderr, end=end, flush=flush)

def get_timestamp():
    return _dt.datetime.now()

def parse_time(time, format=DEFAULT_DATETIME_FORMAT):
    if not isinstance(time, _dt.datetime):
        return _dt.datetime.strptime(str(time), format)
    else:
        return time

def format_time(time, format=DEFAULT_DATETIME_FORMAT):
    return time.strftime(format)

def parse_date(date, format=DEFAULT_DATE_FORMAT):
    return _dt.datetime.strptime(str(date), format)

class BaseObject:
    """
    _fields
    get_field
    set_field
    as_str
    """
    _fields = ()

    def __init__(self, uuid=None):
        self.uuid     = (_uuid.uuid1() if uuid is None else uuid)

    def __getattr__(self, name):
        if name in self._fields:
            return self.get_field(name)
        else:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        if (name == 'uuid') or (name.startswith('_')):
            super().__setattr__(name, value)
        elif name in self._fields:
            self.set_field(name, value)
        else:
            raise AttributeError(f"not settable: {name}")

    def get_field(self, name):
        return getattr(self, '_'+name)

    def set_field(self, name, value):
        setattr(self, '_'+name, value)

    def as_str(self, name):
        return str(getattr(self, '_'+name))

    def for_display(self, name):
        if isinstance(name, int) and (name < len(self._fields)):
            name = self._fields[name]
        elif name not in self._fields:
            raise AttributeError(f"unknown field name: {name}")
        return self.as_str(name)

class Item(BaseObject):
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

    def __init__(self, timestamp=None, category=None, description=None,
                    uuid=None, is_block=False):
        super().__init__(uuid=uuid)
        self._is_block   = is_block
        if is_block == False:
            self._timestamp   = get_timestamp() if timestamp is None else parse_time(timestamp)
            self._description = '' if description is None else description
        self._category    = "Comment" if category is None else category

    def is_block(self):
        return self._is_block

    def as_str(self, name):
        value = getattr(self, '_'+name)
        if name == 'timestamp':
            return format_time(value)
        else:
            return str(value)

    def set_field(self, name, value):
        if name == 'timestamp':
            if not isinstance(value, _dt.datetime):
                value = parse_time(value)
        super().set_field(name, value)

class Block(Item):
    _fields = Item._fields + ('start', 'end',)

    def __init__(self, category=None, content=None, uuid=None):
        super().__init__(category=category, uuid=uuid, is_block=True)
        self._content = content

    def __getattr__(self, name):
        if name == 'content':
            return self._content
        else:
            return super().__getattr__(name)

    def get_description(self):
        return "" if self._content is None else self._content.as_title()

    def get_start(self):
        return None if self._content is None else self._content.get_start()

    def get_end(self):
        return None if self._content is None else self._content.get_end()

    def get_field(self, name):
        if name in ('timestamp', 'start'):
            return self.get_start()
        elif name == 'end':
            return self.get_end()
        elif name == 'description':
            return self.get_description()
        else:
            return super().get_field(name)

    def set_field(self, name, value):
        if name == 'timestamp':
            self.set_field('start', value)
        elif name in ('start', 'stop', 'description'):
            pass
        else:
            super().set_field(name, value)

    def as_str(self, name):
        if name == 'timestamp':
            if self.start is not None:
                return format_time(self.start)
            else:
                return ''
        elif name in ('start', 'stop'):
            return format_time(getattr(self, name))
        elif name == 'description':
            return self.get_description()
        else:
            return str(getattr(self, '_'+name))

class Entity(BaseObject):
    _fields     = ('start', 'end', 'modified',)
    _block      = 'Entity'
    _stamp      = 'datetime'
    _entrycls   = Item
    _parentname = None

    @classmethod
    def parse_start(cls, start):
        if cls._stamp == 'datetime':
            return get_timestamp() if start is None else parse_time(start)
        elif cls._stamp == 'date':
            return None if start is None else parse_date(start)
        else:
            raise ValueError(f"unknown timestamping strategy: {cls._stamp}")

    @classmethod
    def parse_end(cls, end):
        if cls._stamp == 'datetime':
            return None if end is None else parse_time(end)
        elif cls._stamp == 'date':
            return None if end is None else parse_date(end)
        else:
            raise ValueError(f"unknown timestamping strategy: {cls._stamp}")

    def __init__(self, start=None, end=None,
                    modified=None, parent=None, uuid=None):
        super().__init__(uuid=uuid)
        self._start    = self.__class__.parse_start(start)
        self._end      = self.__class__.parse_end(end)
        self._modified = (get_timestamp() if modified is None else parse_time(modified))
        self._parent   = parent
        self._children = []
        self._logs     = []

    def __getattr__(self, name):
        if name == 'logs':
            return self._logs
        elif name == 'title':
            return self.get_title()
        elif name == 'children':
            return self._children
        elif name == self._parentname:
            return self._parent
        else:
            return super().__getattr__(name)

    def __len__(self):
        return len(self._logs)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and (self.uuid == other.uuid)

    def as_entry(self):
        return Block(category=self._block, content=self)

    def get_start(self):
        return self.start

    def get_end(self):
        return self.end

    def get_entry(self, index):
        return self._logs[index]

    def get_title(self):
        return "(untitled)"

    def insert(self, entry, index=-1):
        if index < 0:
            index = len(self._logs)
        if isinstance(entry, Entity):
            self.insert(entry.as_entry(), index=index)
            if entry not in self._children:
                self._children.append(entry)
        elif not isinstance(entry, self._entrycls):
            raise ValueError(f"expected {self._entrycls.__name__}, got {entry.__class__.__name__}")
        else:
            self._logs.insert(index, entry)

    def update(self):
        self.modified = get_timestamp()
        if isinstance(self._parent, Entity):
            self._parent.update()

    def as_str(self, name):
        value = getattr(self, '_'+name)
        if name == 'modified':
            return value.strftime(DEFAULT_DATETIME_FORMAT)
        else:
            return str(value)

    def as_title(self, parents=False):
        if (parents == True) and isinstance(self._parent, Entity):
            return self._parent.as_title(parents=True) + " :: " + self.title
        return self.title
