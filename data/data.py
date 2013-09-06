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

def get(config_get, section, name, default=None):
  try:
    return config_get(section, name)
  except ConfigParser.NoOptionError:
    return default

def config_set(config, section, name, value):
  if value != None:
    config.set(section, name, value)

class Part:

  def __init__(self, cat, fn):
    self.cat = cat
    self.fn = fn
    self.ffn = os.path.join(self.cat.dirname, self.fn)
    self.config = ConfigParser.SafeConfigParser()
    if os.path.exists(self.ffn):
      self.__read_config()

  def set_np(self, name, package):
    self.name = name
    self.package = package
    self.config.add_section('main')
    config_set(self.config, 'main', 'name', self.name)
    config_set(self.config, 'main', 'package', self.package)
    self.full_name = Part.full_name(self.name, self.package)
    with open(self.ffn, 'w+') as f:
      self.config.write(f)

  def __read_config(self):
    if self.config.read(self.ffn) == []:
      raise DataException('file not found ' + self.ffn)
    self.name = get(self.config.get, 'main', 'name')
    self.package = get(self.config.get, 'main', 'package')
    self.full_name = Part.full_name(self.name, self.package)
    self.location = get(self.config.get, 'main','location', '')
    self.footprint = get(self.config.get, 'main','footprint', '')
    self.single_value = get(self.config.getboolean, 'main','single-value', True)
    self.quantity = get(self.config.get, 'main','quantity', '')

  @staticmethod
  def full_name(name, package):
    if name == "":
      raise DataException("name is mandatory")
    fn = name
    if package != "" and package != None:
      fn += '-' + package
    return fn

class Cat:

  def __init__(self, dirname, name=None):
    self.dirname = dirname
    self.file = os.path.join(self.dirname, 'cat.ini')
    self.config = ConfigParser.SafeConfigParser()
    self.prop = {}
    if name is not None:
      self.__make_config()
    else:
      self.__read_config()
    self.parts = self.__scan_parts()

  def __make_config(self):
    if os.path.exists(self.dirname):
      raise DataException("category already exists")
      self.config.add_section('main')
      self.config.set('main', 'name', name)
      os.mkdir(self.dirname)
      with open(self.file, 'w+') as f:
        self.config.write(f)
      self.name = name
  
  def __read_config(self):
    self.config.read(self.file)
    self.name = self.config.get('main', 'name')
    if self.config.has_section('properties'):
      for (k,v) in self.config.items('properties'):
        self.prop[k] = v

  def __scan_parts(self): 
     l = [Part(self, pfn) for pfn in glob.glob(os.path.join(self.dirname, '*.part'))]
     l.sort(key=lambda p:p.name)
     return l

  def __iter__(self):
    return iter(self.parts)

  def part_by_fullname(self, full_name):
    try:
      return next((x for x in self.parts if x.full_name == full_name))
    except StopIteration:
      raise DataException("part not found " + full_name)

  @staticmethod
  def dirname_from_name(name):
    return name.replace(' ','_') + '.cat'

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

  def new_part(self, name, package):
    if name == '':
      raise DataException('name is not optional')
    full_name = Part.full_name(name, package)
    fn = self.unique_fn(full_name)
    part = Part(self, fn)
    part.set_np(name, package)
    return part

class Data:

  def __init__(self, settings):
    self.cat = []
    self.dir = settings.value("basedir", default_basedir)
    if not os.path.isdir(self.dir):
      raise DataException("basedir not a directory")
    g = self.dir + '/*.cat'
    for c in glob.glob(os.path.join(self.dir, '*.cat')):
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


