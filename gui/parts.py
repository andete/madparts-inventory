#!/usr/bin/env python
#
# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

from PySide import QtGui, QtCore
from PySide.QtCore import Qt

class PartTree(QtGui.QTreeView):

  def __init__(self):
    super(PartTree, self).__init__()
    self.model = QtGui.QStandardItemModel()
    self.setModel(self.model)
