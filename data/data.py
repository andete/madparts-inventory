#!/usr/bin/env python
#
# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import os, os.path
import glob
import ConfigParser

default_basedir = "example"

class DataException(Exception):
  pass

class Part:

  def __init__(self, cat, fn):
    self.cat = cat
    self.fn = fn
    self.ffn = os.path.join(self.cat.dirname, self.fn)

class Cat:

  def __init__(self, dirname, name=None):
    self.dirname = dirname
    self.file = os.path.join(self.dirname, 'cat.ini')
    self.config = ConfigParser.SafeConfigParser()
    self.prop = {}
    self.parts = []
    if name is not None:
      if os.path.exists(self.dirname):
        raise DataException("category already exists")
      self.config.add_section('main')
      self.config.set('main', 'name', name)
      os.mkdir(self.dirname)
      with open(self.file, 'w+') as f:
        self.config.write(f)
      self.name = name
    else:
      self.config.read(self.file)
      self.name = self.config.get('main', 'name')
      if self.config.has_section('properties'):
        for (k,v) in self.config.items('properties'):
          self.prop[k] = v

  @staticmethod
  def dirname_from_name(name):
    return name.replace(' ','_') + '.cat'

  @staticmethod
  def file_name_for_part(name, package, value):
    if name == "":
      raise DataException("name is mandatory")
    fn = name
    if package != "":
      fn += '-' + package
    if value != "":
      fn += '-' + value
    return fn

  def unique_fn(self, fn):
    l = glob.glob(os.path.join(self.dirname,"%s-????.part" % fn))
    if l == []:
      return fn + "-0000.part"
    def number(x):
      y = re.search('-(....)\.part', x)
      if y is None:
        return 0
      return int(y)
    n = [number(x) for x in l]
    m = max(n)
    m_res = m
    for i in range(0, m):
      if i not in n:
        m_res = i
        break
    return fn + ("-%04d.part" % m_res)

  def new_part(self, name, package, value):
    fn = Cat.file_name_for_part(name, package, value)
    fn = self.unique_fn(fn)
    print fn
    "TODO data make part"

class Data:

  def __init__(self, settings):
    self.cat = []
    self.dir = settings.value("basedir", default_basedir)
    if not os.path.isdir(self.dir):
      raise DataException("basedir not a directory")
    g = self.dir + '/*.cat'
    #print g, os.getcwd()
    for c in glob.glob(os.path.join(self.dir, '*.cat')):
      #print "adding", c
      self.cat.append(Cat(c))
    self.sort()

  def sort(self):
    self.cat.sort()
  
  def __iter__(self):
    return iter(self.cat)

  def cat_by_name(self, name):
    for x in self.cat:
      if x.name == name:
        return x
    return None

  def new_category(self, name):
    ffn = os.path.join(self.dir, Cat.dirname_from_name(name))
    c = Cat(ffn, name)
    self.cat.append(c)
    self.sort()


