#!/usr/bin/env python
#
# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import os, os.path
import glob
import ConfigParser

# we don't want the interpolation feature
class Config(ConfigParser.RawConfigParser):
  pass

default_basedir = "example"

class DataException(Exception):
  pass

# with default
def wd(d, f):
  try:
    return f()
  except ConfigParser.NoOptionError:
    return d
  
class Part:

  def __init__(self, cat, fn):
    self.cat = cat
    self.fn = fn
    self.ffn = os.path.join(self.cat.dirname, self.fn)
    self.c = Config()
    self.vl = []
    self.bl = []
    self.tl = []
    if os.path.exists(self.ffn):
      self.__read_config()

  def set_np(self, name, package):
    self.name = name
    self.package = package
    self.c.add_section('main')
    self.c.add_section('values')
    self.c.add_section('buy')
    self.c.add_section('tag')
    self.c.set('main', 'name', self.name)
    self.c.set('main', 'package', self.package)
    self.full_name = Part.full_name(self.name, self.package)
    self.full_name_bak = self.full_name
    self.location = ''
    self.footprint = ''
    self.single_value = True
    self.quantity = ''
    self.threshold = ''
    with open(self.ffn, 'w+') as f:
      self.c.write(f)

  def __read_config(self):
    if self.c.read(self.ffn) == []:
      raise DataException('file not found ' + self.ffn)
    self.name = self.c.get('main', 'name')
    self.package = self.c.get('main', 'package')
    self.full_name = Part.full_name(self.name, self.package)
    self.full_name_bak = self.full_name
    self.location = wd('', lambda: self.c.get('main','location'))
    self.footprint = wd('', lambda: self.c.get('main','footprint'))
    self.single_value = wd(True, lambda: self.c.getboolean('main','single-value'))
    self.quantity = wd('', lambda: self.c.get('main','quantity'))
    self.threshold = wd('', lambda: self.c.get('main','threshold'))
    if not self.c.has_section('values'):
      self.c.add_section('values')
    for (k,v) in self.c.items('values'):
      #print (k,v)
      (n, w) = k.split('_')
      n = int(n)
      if w == 'value':
        t = [v]
      elif w == 'quantity':
        t.append(v)
      elif w == 'threshold':
        t.append(v)
        #print t
        self.vl.append((t[0],t[1],t[2]))
    if not self.c.has_section('buy'):
      self.c.add_section('buy')
    for (k,v) in self.c.items('buy'):
      print (k,v)
      (n, w) = k.split('_')
      n = int(n)
      if w == 'when':
        t = [v]
      elif w == 'where':
        t.append(v)
      elif w == 'id':
        t.append(v)
      elif w == 'price':
        t.append(v)
      elif w == 'amount':
        t.append(v)
        self.bl.append((t[0],t[1],t[2],t[3],t[4]))
    if not self.c.has_section('tag'):
      self.c.add_section('tag')
    for (k,v) in self.c.items('tag'):
      print (k,v)
      (n, w) = k.split('_')
      n = int(n)
      if w == 'tag':
        t = [v]
      elif w == 'value':
        t.append(v)
        self.tl.append((t[0],t[1]))

  def save(self):
    print 'saving', self.name
    self.full_name = Part.full_name(self.name, self.package)
    self.c.set('main', 'name', self.name)
    self.c.set('main', 'location', self.location)
    self.c.set('main', 'footprint', self.footprint)
    self.c.set('main', 'single-value', str(self.single_value))
    self.c.set('main', 'quantity', self.quantity)
    self.c.set('main', 'threshold', self.threshold)
    self.c.remove_section('values')
    self.c.add_section('values')
    for i in range(0, len(self.vl)):
      self.c.set('values', "%03d_value" % (i), self.vl[i][0])
      self.c.set('values', "%03d_quantity" % (i), self.vl[i][1])
      self.c.set('values', "%03d_threshold" % (i), self.vl[i][2])
    self.c.remove_section('buy')
    self.c.add_section('buy')
    for i in range(0, len(self.bl)):
      self.c.set('buy', "%03d_when" % (i), self.bl[i][0])
      self.c.set('buy', "%03d_where" % (i), self.bl[i][1])
      self.c.set('buy', "%03d_id" % (i), self.bl[i][2])
      self.c.set('buy', "%03d_price" % (i), self.bl[i][3])
      self.c.set('buy', "%03d_amount" % (i), self.bl[i][4])
    self.c.remove_section('tag')
    self.c.add_section('tag')
    for i in range(0, len(self.tl)):
      self.c.set('tag', "%03d_tag" % (i), self.tl[i][0])
      self.c.set('tag', "%03d_value" % (i), self.tl[i][1])
    with open(self.ffn, 'w+') as f:
      self.c.write(f)
    if self.full_name_bak != self.full_name:
     res = (self.full_name_bak, self.full_name)
     self.full_name_bak = self.full_name
     return res
    return None

  @staticmethod
  def full_name(name, package):
    if name == "":
      raise DataException("name is mandatory")
    fn = name
    if package != "" and package != None:
      fn += '-' + package
    return fn

  def make_full_name(self):
    return Part.full_name(self.name, self.package)

class Cat:

  def __init__(self, dirname, name=None):
    self.dirname = dirname
    self.file = os.path.join(self.dirname, 'cat.ini')
    self.c = Config()
    self.prop = {}
    if name is not None:
      self.__make_config()
    else:
      self.__read_config()
    self.parts = self.__scan_parts()

  def __make_config(self):
    if os.path.exists(self.dirname):
      raise DataException("category already exists")
      self.c.add_section('main')
      self.c.set('main', 'name', name)
      os.mkdir(self.dirname)
      with open(self.file, 'w+') as f:
        self.c.write(f)
      self.name = name
  
  def __read_config(self):
    self.c.read(self.file)
    self.name = self.c.get('main', 'name')
    if self.c.has_section('properties'):
      for (k,v) in self.c.items('properties'):
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
    self.parts.append(part)
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


