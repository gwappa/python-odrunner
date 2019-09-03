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

from pathlib import Path as _Path
from warnings import warn as _warn
from qtpy import QtGui as _QtGui

__root = _Path(__file__).parent / "_rsrc"

if not __root.exists():
    _warn("the odrunner resource file not found. icons may not be properly rendered.")

def resolve(relative_path):
    """returns a string path to the resource file,
    given a path relative to the _rsrc directory"""
    relative_path = _Path(relative_path)
    return str(__root / relative_path)

def as_icon(relative_path):
    """returns the data at the path as a QIcon."""
    return _QtGui.QIcon(resolve(relative_path))
