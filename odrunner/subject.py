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

from qtpy import QtCore as _QtCore
from qtpy.QtCore import Qt as _Qt
from qtpy import QtWidgets as _QtWidgets

from . import core as _core

class Subject(_core.Entity):
    _fields   = ('ID', 'name', 'species', 'strain', 'DOB', 'sex') + _core.Entity._fields
    _entrycls = _core.Item

    def __init__(self, ID=None, name=None,
                    species=None, strain=None, DOB=None, sex=None,
                    modified=None, uuid=None):
        super().__init__(modified=modified, uuid=uuid)
        self.ID      = '' if ID is None else ID
        self.name    = '' if name is None else name
        self.species = '' if species is None else species
        self.strain  = '' if strain is None else strain
        self.DOB     = None if DOB is None else _core.parse_date(DOB)
        self.sex     = 'ND' if sex is None else sex
        self._logs   = []

    def __getattr__(self, name):
        if name == 'logs':
            return self._logs
        else:
            return super().__getattr__(name)

    def __len__(self):
        return len(self._logs)

    def insert(self, entry, index=-1):
        if not isinstance(entry, self._entrycls):
            raise ValueError(f"expected {self._entrycls.__name__}, got {entry.__class__.__name__}")
        self._logs.insert(index, entry)

    def get_log(self, index):
        return self._logs[index]

    def as_title(self):
        if len(self.ID) == 0:
            return "(no name)"
        elif len(self.name) == 0:
            return self.ID
        else:
            return f"{self.ID} ({self.name})"

class View(_QtWidgets.QTableView):
    def __init__(self, subject, logger=None, parent=None):
        super().__init__(parent=parent)
        self.subject = subject
        self._logger = Logger(subject) if logger is None else logger
        self.setModel(self._logger)
        self.horizontalHeader().setStretchLastSection(True)
        self.setWindowTitle(self.subject.as_title())

    def insert(self, entry, index=-1):
        self._logger.insert(entry, index)

class Logger(_QtCore.QAbstractTableModel):
    """the table model for logging of procedures to subjects."""

    def __init__(self, subject, parent=None):
        super().__init__(parent=parent)
        self._entrycls = subject._entrycls
        self._subject  = subject
        self._root     = _QtCore.QModelIndex()

    def headerData(self, section, orientation, role):
        """overrides QAbstractTableModel::headerData."""
        if (orientation == _Qt.Horizontal) and (role == _Qt.DisplayRole):
            return self._entrycls._fields[section]
        else:
            return None

    def rowCount(self, parent):
        """overrides QAbstractTableModel::rowCount."""
        if not parent.isValid():
            # root
            return len(self._subject)
        else:
            return 0

    def columnCount(self, parent):
        """overrides QAbstractTableModel::columnCount."""
        if not parent.isValid():
            # root
            return len(self._entrycls._fields)
        else:
            return 0

    def data(self, index, role):
        if (index.isValid()) and (role == _Qt.DisplayRole):
            return self._subject.get_log(index.row()).for_display(index.column())
        else:
            return None

    def insert(self, entry, index=-1):
        if not isinstance(entry, self._entrycls):
            raise ValueError(f"expected {self._entrycls.__name__}, got {entry.__class__.__name__}")
        index = int(index)
        if index < 0:
            index = len(self._subject) + 1 + index
        self.beginInsertRows(self._root, index, index)
        self._subject.insert(entry, index=index)
        self.endInsertRows()
