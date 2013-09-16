#!/usr/bin/env python
#
# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

from PySide import QtGui, QtCore
from PySide.QtCore import Qt

class Part(QtGui.QStandardItem):

  def __init__(self, catname, name):
    self.name = name
    self.catname = catname
    super(Part, self).__init__(name)
    self.setEditable(False)
    self.setData(('part', catname, name), Qt.UserRole)

  def set_name(self, new):
    self.setText(new)
    self.setData(('part', self.catname, new), Qt.UserRole)
    print 'part renamed to', new
    self.name = new
   

class Category(QtGui.QStandardItem):

  def __init__(self, name):
    self.name = name
    super(Category, self).__init__(name)
    self.setEditable(False)
    self.setData(('category', name, None), Qt.UserRole)

  def add_part(self, name):
    self.appendRow(Part(self.name, name))
    # TODO select new row!

  def rename_part(self, old, new):
    print 'rename_part', old, new
    rc = self.rowCount()
    for i in range(0, rc):
      part_item = self.child(i)
      print part_item.name
      if part_item.name == old:
        part_item.set_name(new)

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

  def __find_cat_item(self, cat_name):
    root = self.invisibleRootItem()
    rc = root.rowCount()
    for i in range(0, rc):
      cat_item = root.child(i)
      (c, name, _) =  cat_item.data(Qt.UserRole)
      if name == cat_name:
        return cat_item
    return None

  def add_part(self, part):
    cat_item = self.__find_cat_item(part.cat.name)
    cat_item.add_part(part.full_name)
    cat_item.sortChildren(0, Qt.AscendingOrder)

  def rename_part(self, cat, old, new):
    print 'rename', cat, old, new
    cat_item = self.__find_cat_item(cat.name)
    cat_item.rename_part(old, new)

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
    (t,cn, n) = current.data(QtCore.Qt.UserRole)
    if t == 'category':
      self.parent.category_selected(cn)
    else:
      self.parent.part_selected(cn, n)
    
