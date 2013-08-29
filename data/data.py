#!/usr/bin/env python
#
# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import os, os.path
import glob
import ConfigParser

default_basedir = "example"

class Cat:

  def __init__(self, dirname, name=None):
    self.dirname = dirname
    self.file = self.dirname + '/cat.ini'
    self.config = ConfigParser.SafeConfigParser()
    if name is not None:
      if os.path.exists(self.dirname):
        raise Exception("category already exists")
      self.config.add_section('main')
      self.config.set('main', 'name', name)
      os.mkdir(self.dirname)
      with open(self.file, 'w+') as f:
        self.config.write(f)
      self.name = name
    else:
      self.config.read(self.file)
      self.name = self.config.get('main', 'name')

  @staticmethod
  def dirname_from_name(name):
    return name.replace(' ','_') + '.cat'

class Data:

  def __init__(self, settings):
    self.cat = []
    self.dir = settings.value("basedir", default_basedir)
    if not os.path.isdir(self.dir):
      raise Exception("basedir not a directory")
    g = self.dir + '/*.cat'
    #print g, os.getcwd()
    for c in glob.glob(self.dir + '/*.cat'):
      #print "adding", c
      self.cat.append(Cat(c))
    self.sort()

  def sort(self):
    self.cat.sort()

  def new_category(self, name):
    c = Cat(self.dir+'/'+Cat.dirname_from_name(name), name)
    self.cat.append(c)
    self.sort()
  
  def __iter__(self):
    return iter(self.cat)
