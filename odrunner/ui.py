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
from qtpy import QtGui as _QtGui

from .core import debug as _debug
from .resources import as_icon as _get_icon

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

class Browser(_QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.__populateActions()
        self.resize(800, 600)
        self.view_stack = []

    def _openSubject(self, checked=None):
        _debug("open...")

    def _newSubject(self, checked=None):
        _debug("new...")

    def _saveSubject(self, checked=None):
        _debug("save...")

    def _dummy(self, checked=None):
        _debug("dummy...")

    def __newAction(self, widget, item):
        action = item['name']
        self.actions[action] = widget.addAction(_get_icon(item['icon']), item['text'])
        self.actions[action].setToolTip(item['tip'])
        self.actions[action].setEnabled(item['init'])
        self.actions[action].triggered.connect(getattr(self, item['slot']))
        if 'key' in item.keys():
            # set shortcut
            self.actions[action].setShortcut(_QtGui.QKeySequence(item['key']))

    def __populateActions(self):
        """setting up application actions"""
        bar = _QtWidgets.QMenuBar(self)
        self.setMenuBar(bar)
        self.menus = {}
        self.menus['__root__'] = bar
        self.actions  = {}
        for info in _commands:
            if info['type'] == 'toolbar':
                widget = _QtWidgets.QToolBar(self)
                widget.setMovable(False)
                widget.setToolButtonStyle(_Qt.ToolButtonTextUnderIcon)
                for item in info['actions']:
                    action = item['name']
                    if action == '__sep__':
                        widget.addSeparator()
                        continue
                    else:
                        self.__newAction(widget, item)
                self.addToolBar(info['position'], widget)
                setattr(self, info['name'], widget)
            elif info['type'] == 'menu':
                name = info['name']
                self.menus[name] = bar.addMenu(info['text'])
                for item in info['actions']:
                    action = item['name']
                    if action == '__sep__':
                        self.menus[name].addSeparator()
                        continue
                    if action in self.actions.keys():
                        self.menus[name].addAction(self.actions[action])
                    else:
                        self.__newAction(self.menus[name], item)
                    if 'key' in item.keys():
                        # set shortcut
                        self.actions[action].setShortcut(_QtGui.QKeySequence(item['key']))
            else:
                continue

_commands = [
    {
        'name': 'browse',
        'type': 'toolbar',
        'position': _Qt.TopToolBarArea,
        'actions': [
            {
                'name': 'prev',
                'icon': 'backward.png',
                'text': 'Go back',
                'tip':  'Back to the parent view',
                'slot': '_dummy',
                'init': False
            },
            {
                'name': 'next',
                'icon': 'forward.png',
                'text': 'Go forward',
                'tip':  'Go to the child view that has been shown previously',
                'slot': '_dummy',
                'init': False
            },
            {
                'name': '__sep__'
            },
            {
                'name': 'edit',
                'icon': 'edit.png',
                'text': 'Edit...',
                'tip':  'Edit the selected entry',
                'slot': '_dummy',
                'init': False
            },
            {
                'name': 'add',
                'icon': 'plus.png',
                'text': 'Add...',
                'tip':  'Add a new entry to the current block',
                'slot': '_dummy',
                'init': False
            },
            {
                'name': 'remove',
                'icon': 'minus.png',
                'text': 'Remove',
                'tip':  'Remove the selected entry',
                'slot': '_dummy',
                'init': False
            }
        ]
    },
    {
        'name': 'operate',
        'type': 'toolbar',
        'position': _Qt.RightToolBarArea,
        'actions': [
            {
                'name': 'new',
                'icon': 'new.png',
                'text': 'New...',
                'tip':  'Create and open a new subject log',
                'slot': '_newSubject',
                'init': True
            },
            {
                'name': 'open',
                'icon': 'open.png',
                'text': 'Open...',
                'tip':  'Open another subject log',
                'slot': '_openSubject',
                'init': True
            },
            {
                'name': 'save',
                'icon': 'save.png',
                'text': 'Save',
                'tip':  'Save the current subject log',
                'slot': '_saveSubject',
                'init': False
            },
            {
                'name': 'close',
                'icon': 'exit.png',
                'text': 'Close',
                'tip':  'Close the current subject log',
                'slot': '_dummy',
                'init': False
            },
            {
                'name': '__sep__'
            },
            {
                'name': 'info',
                'icon': 'info.png',
                'text': 'Info...',
                'tip':  'Show information about this subject',
                'slot': '_dummy',
                'init': False
            }
        ]
    },
    {
        'name': 'file',
        'type': 'menu',
        'text': 'File',
        'actions': [
            {
                'name': 'new',
                'key':  'Ctrl+N'
            },
            {
                'name': 'open',
                'key':  'Ctrl+O'
            },
            {
                'name': 'close',
                'key':  'Ctrl+W'
            },
            {
                'name': '__sep__'
            },
            {
                'name': 'save',
                'key':  'Ctrl+S'
            },
            {
                'name': '__sep__'
            },
            {
                'name': 'info',
                'key':  'Ctrl+I'
            }
        ]
    },
    {
        'name': 'entry',
        'type': 'menu',
        'text': 'Entry',
        'actions': [
            {
                'name': 'add',
                'key':  'Ctrl+Shift+N'
            },
            {
                'name': 'remove',
                'key':  _Qt.CTRL + _Qt.Key_Delete
            },
            {
                'name': '__sep__'
            },
            {
                'name': 'edit',
                'key':  _Qt.CTRL + _Qt.Key_Return
            }
        ]
    },
    {
        'name': 'navigate',
        'type': 'menu',
        'text': 'Navigate',
        'actions': [
            {
                'name': 'prev',
                'key':  'Ctrl+['
            },
            {
                'name': 'next',
                'key':  'Ctrl+]'
            }
        ]
    }
]
