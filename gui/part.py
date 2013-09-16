#!/usr/bin/env python
#
# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

from PySide import QtGui, QtCore
from PySide.QtCore import Qt

class Category(QtGui.QWidget):

  def __init__(self, cat):
    super(Category, self).__init__()
    self.cat = cat
    vbox = QtGui.QVBoxLayout()
    vbox.addWidget(QtGui.QLabel("Category: " + cat.name))
    items = cat.prop.items()
    if len(items) > 0:
      table = QtGui.QTableWidget(len(items), 2)
      table.setHorizontalHeaderLabels(['name','value'])
      p = 0
      for (k,v) in items:
        table.setItem(p,0,QtGui.QTableWidgetItem(k))
        table.setItem(p,1,QtGui.QTableWidgetItem(v))
        p = p + 1
      vbox.addWidget(table)
    self.setLayout(vbox)  

class IntQTableWidgetItem(QtGui.QTableWidgetItem):

  def __init__(self, s):
    super(IntQTableWidgetItem, self).__init__(s)
    self.setFlags(self.flags() & ~(Qt.ItemIsEditable))

  def __lt__(self, other):
    return int(self.text()) < int(other.text())

class Part(QtGui.QWidget):

  def __init__(self, part):
    super(Part, self).__init__()
    self.part = part
    vbox = QtGui.QVBoxLayout()
    part = self.part
    form_layout = QtGui.QFormLayout()
    self.form_layout = form_layout
    def add(k,v,ro=False):
      x = QtGui.QLineEdit(v)
      x.setReadOnly(ro)
      form_layout.addRow(k, x)
      return x
    add("Category", part.cat.name, ro=True)
    self.full_name = add("Part", part.full_name, ro=True)
    self.name = add("Name", part.name)
    self.name.textChanged.connect(self.fn_changed)
    self.package = add("Package", part.package)
    self.package.textChanged.connect(self.fn_changed)
    self.location = add("Location", part.location)
    self.footprint = add('Footprint', part.footprint)
    self.single_value = QtGui.QCheckBox()
    self.single_value.setChecked(part.single_value)
    self.single_value.stateChanged.connect(self.single_value_changed)
    form_layout.addRow('Single-value', self.single_value)
    self.quantity = QtGui.QLineEdit(str(part.quantity))
    self.threshold = QtGui.QLineEdit(str(part.threshold))
    form_layout.addRow('Quantity', self.quantity)
    form_layout.addRow('Threshold', self.threshold)
    if not part.single_value:
      self.quantity.setDisabled(True)
      self.threshold.setDisabled(True)
    vbox.addLayout(form_layout)
    self.valtable = QtGui.QTableWidget(0, 4)
    self.valtable.setHorizontalHeaderLabels(['#', 'value','quantity', 'threshold'])
    self.valtable.itemChanged.connect(self.valtable_item_changed)
    self.valtable.verticalHeader().hide()
    self.valtable.setSortingEnabled(True)
    self.valtable.sortItems(0, Qt.AscendingOrder)
    vbox.addWidget(self.valtable)
    if part.single_value:
     self.valtable.hide()
    else:
      i = 0
      for (val, qua, thr) in part.vl:
        self.valtable.insertRow(i)
        self.valtable.setItem(i, 0, IntQTableWidgetItem(str(i+1)))
        self.valtable.setItem(i, 1, QtGui.QTableWidgetItem(val))
        self.valtable.setItem(i, 2, QtGui.QTableWidgetItem(qua))
        self.valtable.setItem(i, 3, QtGui.QTableWidgetItem(thr))
        i += 1
      self.valtable.insertRow(i)
      self.valtable.setItem(i, 0, QtGui.QTableWidgetItem(str(i+1)))
    vbox.addWidget(QtGui.QLabel("Buy"))
    self.buytable = QtGui.QTableWidget(1, 6)
    self.buytable.setHorizontalHeaderLabels(['when','where','id', 'price','amount','total'])
    self.buytable.setSortingEnabled(True)
    self.buytable.sortItems(0, Qt.AscendingOrder)
    i = 0
    for (when, wher, idx, price, amount) in part.bl:
      self.buytable.insertRow(i)
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
    vbox.addWidget(self.buytable)
    self.setLayout(vbox)

  def single_value_changed(self):
    self.part.single_value = self.single_value.isChecked()
    self.form_layout.itemAt(self.form_layout.getWidgetPosition(self.quantity)[0]).widget().setDisabled(not self.part.single_value)
    self.form_layout.itemAt(self.form_layout.getWidgetPosition(self.threshold)[0]).widget().setDisabled(not self.part.single_value)
    if self.part.single_value:
      self.valtable.hide()
    else:
      self.valtable.show()

  def fn_changed(self):
    self.part.name = self.name.text()
    self.part.package = self.package.text()
    self.full_name.setText(self.part.make_full_name())

  def valtable_item_changed(self, item):
    # automatically expand the value table as it is filled in
    # might need some more intelligence...
    cr = self.valtable.currentRow()
    nr = self.valtable.rowCount()
    #print 'current row:', cr, 'row count:', nr
    if cr == nr - 1:
      self.valtable.insertRow(nr)
      self.valtable.setItem(nr, 0, IntQTableWidgetItem(str(nr+1)))

  def sync(self):
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
    return p.save()
