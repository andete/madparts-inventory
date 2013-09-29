#!/usr/bin/env python
#
# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

from PySide import QtGui, QtCore
from PySide.QtCore import Qt

class Category(QtGui.QWidget):

  def __init__(self):
    super(Category, self).__init__()
    self.name = ""
    self.cat = None
    vbox = QtGui.QVBoxLayout()
    self.name_label = QtGui.QLabel("Category: ")
    vbox.addWidget(self.name_label)
    #items = cat.prop.items()
    self.prop_table = QtGui.QTableWidget(0, 2)
    self.prop_table.setHorizontalHeaderLabels(['name','value'])
    vbox.addWidget(self.prop_table)
    self.setLayout(vbox)  

  def set(self, cat):
    self.cat = cat
    self.name = cat.name
    self.name_label.setText("Category: " + self.name)
    items = cat.prop.items()
    self.prop_table.clear()
    self.prop_table.setHorizontalHeaderLabels(['name','value'])
    self.prop_table.setRowCount(len(items))
    if len(items) > 0:
      p = 0
      for (k,v) in items:
        self.prop_table.setItem(p,0,QtGui.QTableWidgetItem(k))
        self.prop_table.setItem(p,1,QtGui.QTableWidgetItem(v))
        p = p + 1

class IntQTableWidgetItem(QtGui.QTableWidgetItem):

  def __init__(self, s):
    super(IntQTableWidgetItem, self).__init__(s)
    self.setFlags(self.flags() & ~(Qt.ItemIsEditable))

  def __lt__(self, other):
    return int(self.text()) < int(other.text())

class Part(QtGui.QWidget):

  category_changed = QtCore.Signal(str)  

  def __init__(self):
    super(Part, self).__init__()
    self.in_setup = True
    self.part = None
    vbox = QtGui.QVBoxLayout()
    form_layout = QtGui.QFormLayout()
    self.form_layout = form_layout
    self.category_combo = QtGui.QComboBox()
    self.category_combo.setEditable(False)
    self.category_combo.currentIndexChanged.connect(self.category_combo_changed)
    self.form_layout.addRow('Category', self.category_combo)
    def add(k,v,ro=False):
      x = QtGui.QLineEdit(v)
      x.setReadOnly(ro)
      form_layout.addRow(k, x)
      return x
    self.full_name = add("Part", "", ro=True)
    self.name = add("Name", "")
    self.name.textChanged.connect(self.fn_changed)
    self.package = add("Package", "")
    self.package.textChanged.connect(self.fn_changed)
    self.location = add("Location", "")
    self.footprint = add('Footprint', "")
    self.single_value = QtGui.QCheckBox()
    self.single_value.setChecked(False)
    self.single_value.stateChanged.connect(self.single_value_changed)
    form_layout.addRow('Single-value', self.single_value)
    self.quantity = QtGui.QLineEdit("")
    self.threshold = QtGui.QLineEdit("")
    form_layout.addRow('Quantity', self.quantity)
    form_layout.addRow('Threshold', self.threshold)
    vbox.addLayout(form_layout)
    self.valtable = QtGui.QTableWidget(0, 4)
    self.valtable.setHorizontalHeaderLabels(['#', 'value','quantity', 'threshold'])
    self.valtable.itemChanged.connect(self.valtable_item_changed)
    vbox.addWidget(self.valtable)
    vbox.addWidget(QtGui.QLabel("Buy"))
    self.buytable = QtGui.QTableWidget(0, 6)
    self.buytable.setHorizontalHeaderLabels(['when','where','id', 'price','amount','total'])
    self.buytable.setSortingEnabled(True)
    self.buytable.sortItems(0, Qt.AscendingOrder)
    vbox.addWidget(self.buytable)
    self.tagtable = QtGui.QTableWidget(0, 2)
    self.tagtable.setHorizontalHeaderLabels(['tag','value'])
    #self.tagtable.setSortingEnabled(True)
    #self.tagtable.sortItems(0, Qt.AscendingOrder)
    self.tagtable.itemChanged.connect(self.tagtable_item_changed)
    vbox.addWidget(self.tagtable)
    self.setLayout(vbox)

  def set(self, part):
    if part == None:
      self.part = None
      return
    self.in_setup = True
    print "set part:", part.full_name
    self.part = part
    cats = [catx.name for catx in self.part.cat.data.cat]
    cats.sort()
    self.category_combo.clear()
    for cat_name in cats:
      self.category_combo.addItem(cat_name, cat_name)
      if cat_name == self.part.cat.name:
        self.category_combo.setCurrentIndex(self.category_combo.count()-1)
    self.full_name.setText(part.full_name)
    self.name.setText(part.name)
    print "part package:", part.package
    self.package.setText(part.package)
    self.location.setText(part.location)
    self.footprint.setText(part.footprint)
    self.single_value.setChecked(part.single_value)
    self.quantity.setText(part.quantity)
    self.threshold.setText(part.threshold)
    if not part.single_value:
      self.quantity.setDisabled(True)
      self.threshold.setDisabled(True)
    self.valtable.clear()
    self.valtable.setHorizontalHeaderLabels(['#', 'value','quantity', 'threshold'])
    self.valtable.verticalHeader().hide()
    self.valtable.setSortingEnabled(True)
    self.valtable.sortItems(0, Qt.AscendingOrder)
    if part.single_value:
      self.valtable.hide()
    else:
      self.valtable.setRowCount(len(part.vl)+1)
      i = 0
      for (val, qua, thr) in part.vl:
        self.valtable.setItem(i, 0, IntQTableWidgetItem(str(i+1)))
        self.valtable.setItem(i, 1, QtGui.QTableWidgetItem(val))
        self.valtable.setItem(i, 2, QtGui.QTableWidgetItem(qua))
        self.valtable.setItem(i, 3, QtGui.QTableWidgetItem(thr))
        i += 1
      self.valtable.setItem(i, 0, QtGui.QTableWidgetItem(str(i+1)))
    self.buytable.clear()
    self.buytable.setHorizontalHeaderLabels(['when','where','id', 'price','amount','total'])
    self.buytable.setSortingEnabled(True)
    self.buytable.sortItems(0, Qt.AscendingOrder)
    self.valtable.setRowCount(len(part.bl)+1)
    i = 0
    for (when, wher, idx, price, amount) in part.bl:
      self.buytable.setItem(i, 0, QtGui.QTableWidgetItem(when))
      self.buytable.setItem(i, 1, QtGui.QTableWidgetItem(wher))
      self.buytable.setItem(i, 2, QtGui.QTableWidgetItem(idx))
      self.buytable.setItem(i, 3, QtGui.QTableWidgetItem(price))
      self.buytable.setItem(i, 4, QtGui.QTableWidgetItem(amount))
      try:
        total = float(price) * float(amount)
      except ValueError:
        total = 0
      self.buytable.setItem(i, 5, QtGui.QTableWidgetItem(total))
      i += 1
    #self.tagtable.setSortingEnabled(True)
    #self.tagtable.sortItems(0, Qt.AscendingOrder)
    self.tagtable.clear()
    self.tagtable.setRowCount(len(part.tl)+1)
    self.tagtable.setHorizontalHeaderLabels(['tag','value'])
    i = 0
    for (tag, value) in part.tl:
      self.tagtable.setItem(i, 0, QtGui.QTableWidgetItem(tag))
      self.tagtable.setItem(i, 1, QtGui.QTableWidgetItem(value))
      i += 1
    self.in_setup = False

  def single_value_changed(self):
    if self.in_setup:
      return
    self.part.single_value = self.single_value.isChecked()
    self.form_layout.itemAt(self.form_layout.getWidgetPosition(self.quantity)[0]).widget().setDisabled(not self.part.single_value)
    self.form_layout.itemAt(self.form_layout.getWidgetPosition(self.threshold)[0]).widget().setDisabled(not self.part.single_value)
    if self.part.single_value:
      self.valtable.hide()
    else:
      self.valtable.show()

  def fn_changed(self):
    if self.in_setup:
      return
    self.part.name = self.name.text()
    self.part.package = self.package.text()
    self.part.full_name = self.part.make_full_name()
    self.full_name.setText(self.part.full_name)

  def valtable_item_changed(self, item):
    if self.in_setup:
      return
    # automatically expand the value table as it is filled in
    # might need some more intelligence...
    cr = self.valtable.currentRow()
    nr = self.valtable.rowCount()
    #print 'current row:', cr, 'row count:', nr
    if cr == nr - 1:
      self.valtable.insertRow(nr)
      self.valtable.setItem(nr, 0, IntQTableWidgetItem(str(nr+1)))

  def tagtable_item_changed(self, item):
    if self.in_setup:
      return
    cr = self.tagtable.currentRow()
    nr = self.tagtable.rowCount()
    if cr == nr - 1:
      self.tagtable.insertRow(nr)

  def category_combo_changed(self):
    if self.in_setup:
      return
    new_category_name = str(self.category_combo.currentText())
    print "category_combo_changed:", new_category_name, self.part.name
    if new_category_name == self.part.cat.name:
      return
    if new_category_name == "":
      return
    # make sure file is synced to disk first
    self.sync()
    #self.category_combo.currentIndexChanged.disconnect()
    # signal will be caught by mainwin
    self.category_changed.emit(new_category_name)

  def sync(self):
    #print "sync"
    if self.part == None:
      return None
    p = self.part
    p.name = self.name.text()
    p.package = self.package.text()
    p.location = self.location.text()
    p.footprint = self.footprint.text()
    p.single_value = self.single_value.isChecked()
    p.quantity = self.quantity.text()
    p.threshold = self.threshold.text()
    vl = []
    for i in range(0, self.valtable.rowCount()):
       def getval(r, c):
         x = self.valtable.item(r, c)
         if x is None:
           return ''
         return x.text()
       val = getval(i, 1)
       qua = getval(i, 2)
       thr = getval(i, 3)
       if val != '' or qua != '' or thr != '':
         vl.append((val, qua, thr))
    p.vl = vl
    bl = []
    for i in range(0, self.buytable.rowCount()):
       def getval(r, c):
         x = self.buytable.item(r, c)
         if x is None:
           return ''
         return x.text()
       when = getval(i, 0)
       wher = getval(i, 1)
       idx = getval(i, 2)
       price = getval(i, 3)
       amount = getval(i, 4)
       if wher != '':
         bl.append((when, wher, idx, price, amount))
    p.bl = bl
    tl = []
    for i in range(0, self.tagtable.rowCount()):
      def getval(r, c):
        x = self.tagtable.item(r, c)
        if x is None:
          return ''
        return x.text()
      tag = getval(i, 0)
      value = getval(i, 1)
      if tag != '':
        tl.append((tag, value))
    p.tl = tl
    return p.save()
