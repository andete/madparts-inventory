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

  def change_cat(self, new_cat_name):
    self.catname = new_cat_name
    self.setData(('part', new_cat_name, self.name), Qt.UserRole)

class Category(QtGui.QStandardItem):

  def __init__(self, part_model, name):
    self.name = name
    self.part_model = part_model
    super(Category, self).__init__(name)
    self.setEditable(False)
    self.setData(('category', name, None), Qt.UserRole)
    self.hidden_parts = []

  def add_part(self, name):
    new_part = Part(self.name, name)
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
      if not txt in part_item.name:
         to_remove_ind.append(persistant)
      else:
         count += 1
    to_hide_parts = []
    for i in to_remove_ind:
      item = self.takeRow(i.row())[0]
      to_hide_parts.append(item)
    for i in self.hidden_parts:
      if txt in i.name:
        self.appendRow(i)
        count += 1
      else:
        to_hide_parts.append(i)
    self.hidden_parts = to_hide_parts
    return count

class PartModel(QtGui.QStandardItemModel):

  def __init__(self, data):
    super(PartModel, self).__init__()
    self.mdata = data # needs to be called self.mdata as data is an inherited member
    self.setColumnCount(1)
    self.setHorizontalHeaderLabels(['name'])
    self.populate()
    self.sort(0)
    self.being_changed = False
    self.hidden_cats = []

  def set_selection_model(self, selection_model):
    self.selection_model = selection_model

  def populate(self):
    root = self.invisibleRootItem()
    for cat in self.mdata:
      print cat.name
      cat_item = Category(self, cat.name)
      for part in cat:
        cat_item.add_part(part.full_name)
      root.appendRow(cat_item)

  def add_cat(self, cat_name):
    root = self.invisibleRootItem()
    new_cat = Category(self, cat_name)
    root.appendRow(new_cat)
    self.sort(0)
    self.selection_model.select(new_cat.index(), QtGui.QItemSelectionModel.ClearAndSelect)

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

  def __init__(self, model, parent):
    super(PartTree, self).__init__(parent)
    self.parent = parent
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
    _add("&Add Category", parent.add_cat)
    sep = QtGui.QAction(self)
    sep.setSeparator(True)
    self.addAction(sep)
    _add("&Add Part", parent.add_part)
    _add("&Clone Part", parent.clone_part)
    self.expandAll()

  def row_changed(self, current, previous):
    if self.my_model.being_changed:
      return
    (t,cn, n) = current.data(QtCore.Qt.UserRole)
    if t == 'category':
      self.parent.category_selected(cn)
    else:
      self.parent.part_selected(cn, n)
    
