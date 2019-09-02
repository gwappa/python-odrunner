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

from . import core as _core

class Subject(_core.Entity):
    _fields   = ('ID', 'name', 'species', 'strain', 'DOB', 'sex') + _core.Entity._fields
    _block    = "Subject"
    _stamp    = "date"

    def __init__(self, ID=None, name=None, start=None, end=None,
                    species=None, strain=None, DOB=None, sex=None,
                    modified=None, uuid=None):
        super().__init__(start=start, end=end, modified=modified, uuid=uuid)
        self._ID      = '' if ID is None else ID
        self._name    = '' if name is None else name
        self._species = '' if species is None else species
        self._strain  = '' if strain is None else strain
        self._DOB     = None if DOB is None else _core.parse_date(DOB)
        self._sex     = 'ND' if sex is None else sex

    def get_title(self):
        if len(self.ID) == 0:
            return "(no name)"
        elif len(self.name) == 0:
            return self.ID
        else:
            return f"{self.ID} ({self.name})"

class Session(_core.Entity):
    _fields     = ('subject', 'name', 'comment') + _core.Entity._fields
    _block      = "Session"
    _stamp      = "datetime"
    _parentname = 'subject'

    def __init__(self, subject, name, start=None, end=None, comment=None,
                modified=None, uuid=None):
        if subject is None:
            raise ValueError("subject cannot be None for a session")
        if name is None:
            name = "noname" # FIXME
        super().__init__(parent=subject, start=start, end=end, modified=modified, uuid=uuid)
        self._name    = name
        self._comment = '' if comment is None else comment

    def get_title(self):
        return self.name
