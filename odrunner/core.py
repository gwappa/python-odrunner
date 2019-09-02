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

DEFAULT_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DEFAULT_DATE_FORMAT     = "%Y-%m-%d"

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

class Entity(BaseObject):
    _fields = ('modified',)

    def __init__(self, modified=None, parent=None, uuid=None):
        super().__init__(uuid=uuid)
        self.modified = (get_timestamp() if modified is None else parse_time(modified))
        self._parent  = parent

    def mark_modified(self):
        self.modified = get_timestamp()
        if (self._parent is not None) and isinstance(self._parent, Entity):
            self._parent.mark_modified()

    def as_str(self, name):
        value = getattr(self, '_'+name)
        if name == 'modified':
            return value.strftime(DEFAULT_DATETIME_FORMAT)
        else:
            return str(value)


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
            self.timestamp   = get_timestamp() if timestamp is None else parse_time(timestamp)
            self.description = '' if description is None else description
        self.category    = "Comment" if category is None else category

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
    _fields = Item._fields + ('start', 'end', 'children')

    def __init__(self, category=None, start=None, end=None,
                    parent=None, children=None, uuid=None):
        super().__init__(category=category, uuid=uuid, is_block=True)
        self.start     = get_timestamp() if start is None else parse_time(start)
        self.end       = None if end is None else parse_time(end)
        self._parent   = parent
        self._children = [] if children is None else list(children)

    def get_description(self):
        return ""

    def get_field(self, name):
        if name == 'timestamp':
            return self.get_field('start')
        elif name == 'description':
            return self.get_description()
        else:
            return super().get_field(name)

    def set_field(self, name, value):
        if name == 'timestamp':
            self.set_field('start', value)
        elif name in ('start', 'stop'):
            if not isinstance(value, _dt.datetime):
                value = parse_time(value)
            super().set_field(name, value)
        elif name == 'description':
            pass
        else:
            super().set_field(name, value)

    def as_str(self, name):
        if name == 'timestamp':
            return format_time(self.start)
        elif name in ('start', 'stop'):
            return format_time(getattr(self, name))
        elif name == 'description':
            return self.get_description()
        else:
            return str(getattr(self, '_'+name))
