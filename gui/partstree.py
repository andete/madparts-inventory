#!/usr/bin/env python
#
# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

from PySide import QtGui, QtCore
from PySide.QtCore import Qt

class Part(QtGui.QStandardItem):

  def __init__(self, part):
    self.is_part = True
    self.part = part
    name = part.full_name
    catname = part.cat.name
    super(Part, self).__init__(name)
    self.setEditable(False)

  def set_name(self, new):
    self.setText(new)
    print 'part renamed to', new

  def match(self, txt):
    return self.part.match(txt)

class Category(QtGui.QStandardItem):

  def __init__(self, part_model, cat):
    self.is_part = False
    self.cat = cat
    name = self.cat.name
    self.part_model = part_model
    super(Category, self).__init__(name)
    self.setEditable(False)
    self.setData(('category', name, None), Qt.UserRole)
    self.hidden_parts = []

  def add_part(self, part):
    new_part = Part(part)
    self.appendRow(new_part)
    return new_part

  def rename_part(self, old, new):
    print 'rename_part', old, new
    rc = self.rowCount()
    for i in range(0, rc):
      part_item = self.child(i)
      #print part_item.name
      if part_item.name == old:
        part_item.set_name(new)
        return

  def remove_part_item(self, name):
    rc = self.rowCount()
    for i in range(0, rc):
      part_item = self.child(i)
      if part_item.name == name:
        self.removeRow(i)
        return

  def take_part_item(self, name):
    rc = self.rowCount()
    for i in range(0, rc):
      part_item = self.child(i)
      if part_item.name == name:
        return self.takeRow(i)[0]
  
  def add_part_item(self, item):
    self.appendRow(item)

  def filter(self, txt):
    count = 0
    rc = self.rowCount()
    to_remove_ind = []
    for i in range(0, rc):
      part_item = self.child(i)
      model_index = part_item.index()
      persistant = QtCore.QPersistentModelIndex(model_index)
      if not part_item.match(txt):
         to_remove_ind.append(persistant)
      else:
         count += 1
    to_hide_parts = []
    for i in to_remove_ind:
      item = self.takeRow(i.row())[0]
      to_hide_parts.append(item)
    for i in self.hidden_parts:
      if i.match(txt):
        self.appendRow(i)
        count += 1
      else:
        to_hide_parts.append(i)
    self.hidden_parts = to_hide_parts
    return count

class PartModel(QtGui.QStandardItemModel):

  def __init__(self, mdata):
    super(PartModel, self).__init__()
    self.setColumnCount(1)
    self.setHorizontalHeaderLabels(['name'])
    self.populate(mdata)
    self.sort(0)
    self.being_changed = False
    self.hidden_cats = []

  def set_selection_model(self, selection_model):
    self.selection_model = selection_model

  def populate(self, mdata):
    root = self.invisibleRootItem()
    for cat in mdata:
      cat_item = Category(self, cat)
      for part in cat:
        cat_item.add_part(part)
      root.appendRow(cat_item)

  def add_cat(self, cat):
    root = self.invisibleRootItem()
    new_cat = Category(self, cat)
    root.appendRow(new_cat)
    self.sort(0)
    self.selection_model.select(new_cat.index(), QtGui.QItemSelectionModel.ClearAndSelect)

  def __find_cat_item(self, cat_name):
    root = self.invisibleRootItem()
    rc = root.rowCount()
    for i in range(0, rc):
      cat_item = root.child(i)
      if name == cat_item.cat.name:
        return cat_item
    return None

  def add_part(self, part):
    cat_item = self.__find_cat_item(part.cat.name)
    new_part = cat_item.add_part(part.full_name)
    cat_item.sortChildren(0, Qt.AscendingOrder)
    self.selection_model.select(new_part.index(), QtGui.QItemSelectionModel.ClearAndSelect)
 
  def rename_part(self, cat, old, new):
    print 'rename', cat, old, new
    cat_item = self.__find_cat_item(cat.name)
    cat_item.rename_part(old, new)

  def move_part(self, old_cat_name, part):
    self.being_changed = True
    old_cat_item = self.__find_cat_item(old_cat_name)
    item = old_cat_item.take_part_item(part.full_name)
    item.change_cat(part.cat.name)
    new_cat_item = self.__find_cat_item(part.cat.name)
    new_cat_item.add_part_item(item)
    #new_cat_item.sortChildren(0, Qt.AscendingOrder)
    self.selection_model.select(item.index(), QtGui.QItemSelectionModel.ClearAndSelect)
    self.being_changed = False

  def filter(self, txt):
    try:
      self.being_changed = True
      root = self.invisibleRootItem()
      rc = root.rowCount()
      to_remove_ind = []
      for i in range(0, rc):
        cat_item = root.child(i)
        if cat_item.filter(txt) == 0:
          to_remove_ind.append(QtCore.QPersistentModelIndex(cat_item.index()))
      to_hide_cats = []
      for i in to_remove_ind:
        item = self.takeRow(i.row())[0]
        to_hide_cats.append(item)
      for i in self.hidden_cats:
        if i.filter(txt) > 0:
          self.appendRow(i)
        else:
          to_hide_cats.append(i)
      self.hidden_cats = to_hide_cats
    finally:
      self.sort(0)
      self.tree.expandAll()
      self.being_changed = False

class PartTree(QtGui.QTreeView):

  def __init__(self, model, mainwin):
    super(PartTree, self).__init__()
    self.mainwin = mainwin
    self.setModel(model)
    self.my_model = model
    self.my_model.tree = self
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
    _add("&Add Category", mainwin.add_cat)
    sep = QtGui.QAction(self)
    sep.setSeparator(True)
    self.addAction(sep)
    _add("&Add Part", mainwin.add_part)
    _add("&Clone Part", mainwin.clone_part)
    self.expandAll()

  def row_changed(self, current, previous):
    if self.my_model.being_changed:
      return
    item = self.my_model.itemFromIndex(current)
    if item is None:
      return
    if item.is_part:
      self.mainwin.part_selected(item.part)
    else:
      self.mainwin.category_selected(item.cat)
    
