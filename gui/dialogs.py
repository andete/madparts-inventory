#!/usr/bin/env python
#
# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

from PySide import QtGui, QtCore
from PySide.QtCore import Qt

import re

from data.data import default_basedir, DataException

class PreferencesDialog(QtGui.QDialog):

  def __init__(self, parent, settings):
    super(PreferencesDialog, self).__init__(parent)
    self.setWindowTitle('Preferences')
    self.resize(640,160)
    vbox = QtGui.QVBoxLayout()
    form_layout = QtGui.QFormLayout()
    
    self.dir = settings.value("basedir", default_basedir)
    self.git_push = settings.value("git_push", "True") == "True"
    self.settings = settings

    def dir_select_widget():
      hbox = QtGui.QHBoxLayout()
      widget = QtGui.QWidget()
      lib_button = QtGui.QPushButton("Browse")
      lib_button.clicked.connect(self.browse)
      hbox.addWidget(lib_button)
      self.dir_widget = QtGui.QLineEdit(self.dir)
      self.dir_widget.setReadOnly(True)
      hbox.addWidget(self.dir_widget)
      widget.setLayout(hbox)
      return widget

    self.dir_select = dir_select_widget()

    form_layout.addRow("base directory", self.dir_select)
    form_layout.addRow("warning", QtGui.QLabel("(Need to restart program after changing base directory!)"))

    self.git_push_checkbox = QtGui.QCheckBox()
    self.git_push_checkbox.setChecked(self.git_push)
    form_layout.addRow("git push", self.git_push_checkbox)

    vbox.addLayout(form_layout)
    buttons = QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.RestoreDefaults | QtGui.QDialogButtonBox.Cancel
    button_box = QtGui.QDialogButtonBox(buttons, QtCore.Qt.Horizontal)
    rest_but = button_box.button(QtGui.QDialogButtonBox.RestoreDefaults)
    rest_but.setDisabled(True)
    #rest_but.clicked.connect(self.settings_restore_defaults)
    button_box.accepted.connect(self.accept)
    button_box.rejected.connect(self.reject)
    vbox.addWidget(button_box)
    self.setLayout(vbox)

  def accept(self):
    self.settings.setValue("basedir", self.dir_widget.text())
    self.git_push = self.git_push_checkbox.isChecked()
    self.settings.setValue("git_push", str(self.git_push))
    super(PreferencesDialog, self).accept()

  def browse(self):
    result = QtGui.QFileDialog.getExistingDirectory(self, "Select base directory")
    if result == '': return
    self.dir_widget.setText(result)

class AddCatDialog(QtGui.QDialog):

  def __init__(self, parent, data):
    super(AddCatDialog, self).__init__(parent)
    self.data = data
    self.setWindowTitle('Add Category')
    self.resize(640,160)
    vbox = QtGui.QVBoxLayout()
    form_layout = QtGui.QFormLayout()
    self.name_edit = QtGui.QLineEdit()
    form_layout.addRow("Name: ", self.name_edit)
    vbox.addLayout(form_layout)
    buttons = QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel
    button_box = QtGui.QDialogButtonBox(buttons, QtCore.Qt.Horizontal)
    button_box.accepted.connect(self.accept)
    button_box.rejected.connect(self.reject)
    vbox.addWidget(button_box)
    self.setLayout(vbox)

  def accept(self):
    name = self.name_edit.text()
    try:
      self.result = self.data.new_category(name)
      super(AddCatDialog, self).accept()
    except DataException as e:
      QtGui.QMessageBox.critical(self, "error", str(e))


class AddPartDialog(QtGui.QDialog):

  def __init__(self, parent, data, cat):
    super(AddPartDialog, self).__init__(parent)
    self.data = data
    self.cat = cat
    self.setWindowTitle('Add Part')
    self.resize(640,160)
    vbox = QtGui.QVBoxLayout()
    form_layout = QtGui.QFormLayout()
    self.name_edit = QtGui.QLineEdit()
    form_layout.addRow("Category: ", QtGui.QLabel(self.cat.name))
    form_layout.addRow("Name: ", self.name_edit)
    self.package_edit = QtGui.QLineEdit()
    form_layout.addRow("Package: ", self.package_edit)
    vbox.addLayout(form_layout)
    buttons = QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel
    button_box = QtGui.QDialogButtonBox(buttons, QtCore.Qt.Horizontal)
    button_box.accepted.connect(self.accept)
    button_box.rejected.connect(self.reject)
    vbox.addWidget(button_box)
    self.setLayout(vbox)

  def accept(self):
    name = self.name_edit.text().strip().replace(' ','_')
    package = self.package_edit.text().strip().replace(' ','_')
    self.result = None
    try:
      self.result = self.cat.new_part(name, package)
      super(AddPartDialog, self).accept()
    except DataException as e:
      QtGui.QMessageBox.critical(self, "error", str(e))

class ClonePartDialog(QtGui.QDialog):

  def __init__(self, parent, data, part):
    super(ClonePartDialog, self).__init__(parent)
    self.to_clone_part = part
    self.setWindowTitle('Clone Part')
    self.resize(640,160)
    vbox = QtGui.QVBoxLayout()
    form_layout = QtGui.QFormLayout()
    form_layout.addRow("Category: ", QtGui.QLabel(part.cat.name))
    self.name_edit = QtGui.QLineEdit(part.name)
    form_layout.addRow("Name: ", self.name_edit)
    self.package_edit = QtGui.QLineEdit(part.package)
    form_layout.addRow("Package: ", self.package_edit)
    vbox.addLayout(form_layout)
    buttons = QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel
    button_box = QtGui.QDialogButtonBox(buttons, QtCore.Qt.Horizontal)
    button_box.accepted.connect(self.accept)
    button_box.rejected.connect(self.reject)
    vbox.addWidget(button_box)
    self.setLayout(vbox)

  def accept(self):
    name = self.name_edit.text().strip().replace(' ','_')
    package = self.package_edit.text().strip().replace(' ','_')
    self.result = None
    try:
      self.result = self.to_clone_part.cat.clone_part(self.to_clone_part, name, package)
      self.result.save()
      super(ClonePartDialog, self).accept()
    except DataException as e:
      QtGui.QMessageBox.critical(self, "error", str(e))
