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

  @property
  def name(self):
    return self.part.full_name

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
      if part_item.name == new:
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

class InternalPartModel(QtGui.QStandardItemModel):

  def __init__(self, mdata, sort_model):
    super(InternalPartModel, self).__init__()
    self.setColumnCount(1)
    self.setHorizontalHeaderLabels(['name'])
    self.populate(mdata)
    self.being_changed = False
    self.hidden_cats = []
    self.sort_model = sort_model

  def sort(self):
    self.sort_model.sort(0)

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
    return new_cat

  def __find_cat_item(self, cat_name):
    root = self.invisibleRootItem()
    rc = root.rowCount()
    for i in range(0, rc):
      cat_item = root.child(i)
      if cat_name == cat_item.cat.name:
        return cat_item
    return None

  def add_part(self, part):
    cat_item = self.__find_cat_item(part.cat.name)
    new_part = cat_item.add_part(part)
    return new_part
 
  def rename_part(self, cat, old, new):
    print 'rename', cat.name, old, new
    cat_item = self.__find_cat_item(cat.name)
    cat_item.rename_part(old, new)

  def move_part(self, old_cat_name, part):
    self.being_changed = True
    old_cat_item = self.__find_cat_item(old_cat_name)
    item = old_cat_item.take_part_item(part.full_name)
    new_cat_item = self.__find_cat_item(part.cat.name)
    new_cat_item.add_part_item(item)
    self.being_changed = False
    return item

class PartModel(QtGui.QSortFilterProxyModel):

  def __init__(self, mdata):
    super(PartModel, self).__init__()
    self.ip = InternalPartModel(mdata, self)
    self.setSourceModel(self.ip)
    self.setDynamicSortFilter(True)
    self.sort(0)
    self.filter_txt = ""
    self.selection_model = None

  def lessThan(self, left, right):
    leftData = self.sourceModel().data(left)
    rightData = self.sourceModel().data(right)
    #print leftData, rightData
    return leftData.lower() < rightData.lower()

  def filterAcceptsRow(self, source_row, source_parent):
    # always accept Categories
    #print "filterAcceptsRow", source_row, source_parent
    source_parent_item = self.ip.itemFromIndex(source_parent)
    if source_parent_item is None: 
      return True
    item = source_parent_item.child(source_row)
    if item is None:
      return True
    if not item.is_part:
      return True
    return item.match(self.filter_txt)
    #return super(PartModel, self).filterAcceptsRow(source_row, source_parent)

  def being_changed(self):
    return self.ip.being_changed

  def itemFromIndex(self, current):
    return self.ip.itemFromIndex(self.mapToSource(current))

  def set_selection_model(self, selmod):
    self.selection_model = selmod

  def make_selection_model(self, tree):
    return QtGui.QItemSelectionModel(self, tree)

  def add_part(self, part):
    new_part = self.ip.add_part(part)
    self.sort(0)
    i = self.mapFromSource(new_part.index())
    self.selection_model.select(i, QtGui.QItemSelectionModel.ClearAndSelect)

  def add_cat(self, cat):
    new_cat = self.ip.add_cat(part)
    self.sort(0)
    i = self.mapFromSource(new_cat.index())
    self.selection_model.select(i, QtGui.QItemSelectionModel.ClearAndSelect)
  
  def move_part(self, old_cat_name, part):
    new_part = self.ip.move_part(old_cat_name, part)
    self.sort(0)
    i = self.mapFromSource(new_part.index())
    self.selection_model.select(i, QtGui.QItemSelectionModel.ClearAndSelect)

  def filter(self, txt):
    self.filter_txt = txt
    try:
      self.ip.being_changed = True
      self.setFilterFixedString(txt)
    finally:
      self.sort(0)
      self.tree.expandAll()
      self.ip.being_changed = False

  
class PartTree(QtGui.QTreeView):

  def __init__(self, model, mainwin):
    super(PartTree, self).__init__()
    self.mainwin = mainwin
    self.setModel(model)
    self.my_model = model
    self.my_model.tree = self
    self.selection_model = model.make_selection_model(self)
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
    if self.my_model.being_changed():
      return
    item = self.my_model.itemFromIndex(current)
    if item is None:
      print "non item"
      return
    if item.is_part:
      self.mainwin.part_selected(item.part)
    else:
      self.mainwin.category_selected(item.cat)
    
