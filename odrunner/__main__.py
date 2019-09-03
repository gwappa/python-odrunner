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

from qtpy import QtWidgets as _QtWidgets
import sys as _sys

# from . import open, Item, Block, Subject, Session
from .ui import Browser

def run():
    app = _QtWidgets.QApplication(_sys.argv)
    # subject = Subject(ID='MLA-11211', name="S001/20")
    # session = Session(subject, name="190905-1")
    # subject.insert(Item(category="Comment", description="this is a comment."))
    # subject.insert(Item(category="Comment", description="this is another comment."))
    # subject.insert(session)
    # view = open(subject, as_window=True)
    browser = Browser()
    browser.show()
    _sys.exit(app.exec())

if __name__ == '__main__':
    run()
