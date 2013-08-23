#!/usr/bin/env python
#
# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

from PySide import QtGui, QtCore
from PySide.QtCore import Qt

class PreferencesDialog(QtGui.QDialog):

  def __init__(self, parent, settings):
    super(PreferencesDialog, self).__init__(parent)
    vbox = QtGui.QVBoxLayout()
    form_layout = QtGui.QFormLayout()
    
    self.dir = settings.value("basedir", "example")
    self.settings = settings

    def dir_select_widget():
      hbox = QtGui.QHBoxLayout()
      widget = QtGui.QWidget()
      lib_button = QtGui.QPushButton("Browse")
      hbox.addWidget(lib_button)
      self.dir_widget = QtGui.QLineEdit(self.dir)
      self.dir_widget.setReadOnly(True)
      hbox.addWidget(self.dir_widget)
      widget.setLayout(hbox)
      return widget

    self.dir_select = dir_select_widget()

    form_layout.addRow("base directory", self.dir_select) 
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
    super(PreferencesDialog, self).accept()

