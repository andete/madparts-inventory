#!/usr/bin/env python
#
# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

from PySide import QtGui, QtCore
from PySide.QtCore import Qt

class Part(QtGui.QStandardItem):

  def __init__(self, name):
    self.name = name
    super(Part, self).__init__(name)
    self.setEditable(False)
    self.setData(('part', name), Qt.UserRole)

class Category(QtGui.QStandardItem):

  def __init__(self, name):
    self.name = name
    super(Category, self).__init__(name)
    self.setEditable(False)
    self.setData(('category', name), Qt.UserRole)

  def add_part(self, name):
    self.appendRow(Part(name))

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
      cat_item = Category(cat.name)
      for part in cat:
        cat_item.add_part(part.full_name)
      root.appendRow(cat_item)

  def add_cat(self, cat_name):
    root = self.invisibleRootItem()
    root.appendRow(Category(cat_name))
    self.sort(0)

  def add_part(self, part):
    root = self.invisibleRootItem()
    rc = root.rowCount()
    for i in range(0, rc):
      cat_item = root.child(i)
      (c, name) = cat_item.getData(Qt.UserRole)
      if name == part.cat.name:
        cat_item.add_part(part.full_name)
        cat_item.sort(0)
        break

class PartTree(QtGui.QTreeView):

  def __init__(self, model, parent):
    super(PartTree, self).__init__(parent)
    self.parent = parent
    self.setModel(model)
    self.selection_model = QtGui.QItemSelectionModel(model, self)
    self.selection_model.currentRowChanged.connect(self.row_changed)
    self.setSelectionModel(self.selection_model)
    self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
    def _add(text, slot = None, shortcut = None):
      action = QtGui.QAction(text, self)
      self.addAction(action)
      if slot != None: 
        action.triggered.connect(slot)
      else: 
        action.setDisabled(True)
      if shortcut != None: 
        action.setShortcut(shortcut)
    _add("&Add Category", parent.add_cat)
    sep = QtGui.QAction(self)
    sep.setSeparator(True)
    self.addAction(sep)
    _add("&Add Part", parent.add_part)
    self.expandAll()

  def row_changed(self, current, previous):
    (t,n) = current.data(QtCore.Qt.UserRole)
    if t == 'category':
      self.parent.category_selected(n)
    else:
      self.parent.part_selected(n)
    
