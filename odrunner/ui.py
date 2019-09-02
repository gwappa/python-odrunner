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

from .core import debug as _debug

class TableView(_QtWidgets.QTableView):
    def __init__(self, data, logger=None, parent=None):
        super().__init__(parent=parent)
        self.data    = data
        self._logger = LogDataModel(data) if logger is None else logger
        self.setModel(self._logger)
        self._logger.checkedError.connect(self.showErrorDialog)
        self.setSelectionBehavior(_QtWidgets.QAbstractItemView.SelectRows)
        self.horizontalHeader().setStretchLastSection(True)
        self.doubleClicked.connect(self.openEntry)

    def insert(self, entry, index=-1):
        self._logger.insert(entry, index)

    def openEntry(self, index):
        entry = self._logger.getEntryAt(index)
        if (entry is not None) and entry.is_block():
            _debug(f"opening: {entry}")
            openEntity(entry.content, as_window=True)
        # TODO: ignore all the primitive entries?

    def showErrorDialog(self, title, msg):
        _QtWidgets.QMessageBox.warning(self, title, msg)


class LogDataModel(_QtCore.QAbstractTableModel):
    """the table model for logging of procedures to subjects."""
    checkedError = _QtCore.Signal(str, str)

    def __init__(self, data, parent=None):
        super().__init__(parent=parent)
        self._entrycls = data._entrycls
        self._data     = data
        self._root     = _QtCore.QModelIndex()

    def headerData(self, section, orientation, role):
        """overrides QAbstractTableModel::headerData."""
        if (orientation == _Qt.Horizontal) and (role == _Qt.DisplayRole):
            return self.columnName(section)
        else:
            return None

    def columnName(self, index):
        return self._entrycls._fields[index]

    def rowCount(self, parent):
        """overrides QAbstractTableModel::rowCount."""
        if not parent.isValid():
            # root
            return len(self._data)
        else:
            return 0

    def columnCount(self, parent):
        """overrides QAbstractTableModel::columnCount."""
        if not parent.isValid():
            # root
            return len(self._entrycls._fields)
        else:
            return 0

    def flags(self, index):
        base = super().flags(index)
        if (index.isValid()) and (not self._data.get_entry(index.row()).is_block()):
            if self.columnName(index.column()) != 'category':
                return base | _Qt.ItemIsEditable
        return base

    def data(self, index, role):
        if index.isValid():
            if role in (_Qt.DisplayRole, _Qt.EditRole):
                return self._data.get_entry(index.row()).for_display(index.column())
            else:
                return None
        else:
            return None

    def setData(self, index, value, role):
        entry = self._data.get_entry(index.row())
        try:
            entry.set_field(self._entrycls._fields[index.column()], value)
            return True
        except ValueError as e:
            self.checkedError.emit("Input error", str(e))
            return False

    def getEntryAt(self, index):
        if index.isValid():
            return self._data.get_entry(index.row())
        else:
            return None

    def insert(self, entry, index=-1):
        if not isinstance(entry, self._entrycls):
            raise ValueError(f"expected {self._entrycls.__name__}, got {entry.__class__.__name__}")
        index = int(index)
        if index < 0:
            index = len(self._data) + 1 + index
        self.beginInsertRows(self._root, index, index)
        self._data.insert(entry, index=index)
        self.endInsertRows()

_views = []

def openEntity(entity, parent=None, as_window=True):
    view = TableView(entity, parent=parent)
    view.setWindowTitle(entity.as_title(parents=True))
    if as_window == True:
        view.resize(600, 400)
        view.show()
        _views.append(view)
    return view