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
    add("Part", part.full_name, ro=True)
    self.name = add("Name", part.name)
    self.package = add("Package", part.package)
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
    self.valtable = QtGui.QTableWidget(1, 3)
    self.valtable.setHorizontalHeaderLabels(['value','quantity', 'threshold'])
    vbox.addWidget(self.valtable)
    if part.single_value:
       self.valtable.hide()
    vbox.addWidget(QtGui.QLabel("Buy"))
    buytable = QtGui.QTableWidget(1, 6)
    buytable.setHorizontalHeaderLabels(['when','where','id', 'price','amount','total'])
    vbox.addWidget(buytable)
    self.setLayout(vbox)

  def single_value_changed(self):
    self.part.single_value = self.single_value.isChecked()
    self.form_layout.itemAt(self.form_layout.getWidgetPosition(self.quantity)[0]).widget().setDisabled(not self.part.single_value)
    self.form_layout.itemAt(self.form_layout.getWidgetPosition(self.threshold)[0]).widget().setDisabled(not self.part.single_value)
    if self.part.single_value:
      self.valtable.hide()
    else:
      self.valtable.show()

  def sync(self):
    print "TODO sync to data part"
    p = self.part
    p.package = self.package.text()
    p.location = self.location.text()
    p.footprint = self.footprint.text()
    p.single_value = self.single_value.isChecked()
    p.quantity = self.quantity.text()
    p.threshold = self.threshold.text()
    # TODO more
    p.save()
