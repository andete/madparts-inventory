#!/usr/bin/env python
#
# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

from PySide import QtGui, QtCore
from PySide.QtCore import Qt

class Category(QtGui.QStandardItem):

  def __init__(self, name):
    self.name = name
    super(Category, self).__init__(name)
    self.setEditable(False)
    self.setData(('category', name), Qt.UserRole)

class PartModel(QtGui.QStandardItemModel):

  def __init__(self, data):
    super(PartModel, self).__init__()
    self.mdata = data # needs to be called self.mdata as data is an inherited member
    self.setColumnCount(1)
    self.setHorizontalHeaderLabels(['name'])
    self.populate()
    self.sort(0)

  def populate(self):
    root = self.invisibleRootItem()
    for cat in self.mdata:
      print cat.name
      root.appendRow(Category(cat.name))

  def add(self, cat_name):
    root = self.invisibleRootItem()
    root.appendRow(Category(cat_name))
    self.sort(0)
     

class PartTree(QtGui.QTreeView):

  def __init__(self, model, parent):
    super(PartTree, self).__init__(parent)
    self.parent = parent
    self.setModel(model)
    self.selection_model = QtGui.QItemSelectionModel(model, self)
    self.selection_model.currentRowChanged.connect(self.row_changed)
    self.setRootIsDecorated(False)
    self.setSelectionModel(self.selection_model)
    self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
    def _add(text, slot = None):
      action = QtGui.QAction(text, self)
      self.addAction(action)
      if slot != None: action.triggered.connect(slot)
      else: action.setDisabled(True)
    _add("&Add Category", parent.add_cat)
    sep = QtGui.QAction(self)
    sep.setSeparator(True)
    self.addAction(sep)
    _add("&Add Part", parent.add_part)

  def row_changed(self, current, previous):
    (t,n) = current.data(QtCore.Qt.UserRole)
    if t == 'category':
      self.parent.category_selected(n)
    else:
      self.parent.part_selected(n)
    
