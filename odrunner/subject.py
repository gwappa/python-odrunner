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

from . import LogEntry as _BaseEntry

class Entry(_BaseEntry):
    pass

class View(_QtWidgets.QTableView):
    def __init__(self, subject, logger=None, parent=None):
        super().__init__(parent=parent)
        self.name    = subject
        self._logger = Logger() if logger is None else logger
        self.setModel(self._logger)
        self.horizontalHeader().setStretchLastSection(True)
        self.setWindowTitle(self.name)

    def insert(self, entry, index=-1):
        self._logger.insert(entry, index)

class Logger(_QtCore.QAbstractTableModel):
    """the table model for logging of procedures to subjects."""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._entrycls = Entry
        self._entries  = []
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
            return len(self._entries)
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
            return self._entries[index.row()].display_field(index.column())
        else:
            return None

    def insert(self, entry, index=-1):
        if not isinstance(entry, self._entrycls):
            raise ValueError(f"expected {self._entrycls.__name__}, got {entry.__class__.__name__}")
        index = int(index)
        if index < 0:
            index = len(self._entries) + 1 + index
        self.beginInsertRows(self._root, index, index)
        self._entries.insert(index, entry)
        self.endInsertRows()
