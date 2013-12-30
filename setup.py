#!/usr/bin/env python
#
# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

VERSION='0.1.0'

import glob, sys, platform

from setuptools import setup

with open('README.md') as file:
    long_description = file.read()

arch = platform.uname()[4]

extra_data_files = []

if sys.platform == 'darwin':
  OPTIONS = {
      'argv_emulation': True,
      #'includes': ['sip', 'PyQt4', 'PyQt4.QtCore', 'PyQt4.QtGui', 'simplejson'],
      #'excludes': ['PyQt4.QtDesigner', 'PyQt4.QtNetwork', 'PyQt4.QtOpenGL', 'PyQt4.QtScript', 'PyQt4.QtSql', 'PyQt4.QtTest', 'PyQt4.QtWebKit', 'PyQt4.QtXml', 'PyQt4.phonon'],
      }
  extra_options = dict(
      setup_requires=['py2app'],
      app=['madinv'],
      # Cross-platform applications generally expect sys.argv to
      # be used for opening files.
      options=dict(py2app=OPTIONS),
      )
elif sys.platform.startswith('linux'):
   extra_options = dict(
       # Normally unix-like platforms will use "setup.py install"
       # and install the main script as such
       scripts=['madinv'],
       )
   if not arch in ['x86_64']:
     raise Exception("unsupported arch %s" % (arch))
else:
  raise Exception("unsupported platform %s" % (sys.platform))

setup(
  name = 'madinv',
  description = 'a functional footprint editor',
  long_description = long_description,
  author = 'Joost Yervante Damad',
  author_email = 'joost@damad.be',
  version = VERSION,
  url = 'http://madparts.org/',
  packages = [
        'data',
        'gui',
        ],
  package_data= { 
        'gui': [
          '../COPYING', '../README.md', # dirty trick ;)
          ],
        },
  data_files = [
    ('share/madinv/example', glob.glob('example/README.md')),
    ('share/madinv/example/Connectors.cat', glob.glob('example/Connectors.cat/*')),
    ('share/madinv/example/Discretes.cat', glob.glob('example/Discretes.cat/*')),
    ('share/madinv/example/Opto.cat', glob.glob('example/Opto.cat/*')),
    ('share/madinv/example/ICs.cat', glob.glob('example/ICs.cat/*')),
    ('share/madinv/example/Passives.cat', glob.glob('example/Passives.cat/*')),
    ] + extra_data_files,
  platforms = ["Linux", "Mac OS-X"],
  **extra_options
  )
