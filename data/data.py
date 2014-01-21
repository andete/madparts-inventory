#!/usr/bin/env python
#
# (c) 2013-2014 Joost Yervante Damad <joost@damad.be>
# License: GPL

import os, os.path, copy, shutil, re
import glob, datetime
import ini

default_basedir = "example"

class DataException(Exception):
  pass

# part proxy
class Part(object):
  
  def __init__(self, cat):
    self.cat = cat

  @staticmethod
  def make(cat, fn):
    part = Part(cat)
    part.p = ini.Part(cat, fn)
    part.__set_tags()
    part.full_name_bak = part.full_name
    return part

  def save(self):
    self.p.save()
    res = None
    if self.full_name_bak  != self.full_name:
      res = (self.full_name_bak, self.full_name)
    self.full_name_bak = self.full_name
    self.__set_tags()
    return res

  def clone(self, name, package, fn):
    new_part = Part(self.cat)
    new_part.p = self.p.clone(name, package, fn)
    new_part.__set_tags()
    new_part.full_name_bak = new_part.full_name
    return new_part

  @property
  def name(self):
     return self.p.name

  @name.setter
  def name(self, value):
     self.p.name = value

  @property
  def package(self):
     return self.p.package

  @package.setter
  def package(self, value):
     self.p.package = value

  @property
  def location(self):
     return self.p.location

  @location.setter
  def location(self, value):
     self.p.location = value

  @property
  def footprint(self):
     return self.p.footprint

  @footprint.setter
  def footprint(self, value):
     self.p.footprint = value

  @property
  def quantity(self):
     return self.p.quantity

  @quantity.setter
  def quantity(self, value):
     self.p.quantity = value

  @property
  def threshold(self):
     return self.p.threshold

  @threshold.setter
  def threshold(self, value):
     self.p.threshold = value

  @property
  def last_changed(self):
     return self.p.last_changed

  @property
  def single_value(self):
     return self.p.single_value

  @single_value.setter
  def single_value(self, value):
     self.p.single_value = value

  # TODO better names for these!
  @property
  def vl(self):
     return self.p.vl

  @property
  def bl(self):
     return self.p.bl

  @property
  def tl(self):
     return self.p.tl

  @staticmethod
  def calc_full_name(name, package):
    if name == "":
      raise DataException("name is mandatory")
    fn = name
    if package != "" and package != None:
      fn += '-' + package
    return fn

  @property
  def full_name(self):
    return Part.calc_full_name(self.name, self.package)

  def __set_tags(self):
    self.tags = []
    self.tags.append(self.full_name.lower())
    self.tags.append(self.location.lower())
    for (k,v) in self.tl:
      if k != "":
        self.tags.append(k.lower())
      if v != "":
        self.tags.append(v.lower())

  def match(self, txt):
    for x in self.tags:
      if txt in x:
        return True
    return False


class Cat:

  def __init__(self, data, dirname, name=None):
    self.data = data
    self.dirname = dirname
    self.file = os.path.join(self.dirname, 'cat.ini')
    self.c = ini.Config()
    self.prop = {}
    if name is not None:
      self.__make_config(name)
    else:
      self.__read_config()
    self.parts = self.__scan_parts()

  def __repr__(self):
    return "Cat(%s,%s)" % (self.name, self.dirname)

  def __make_config(self, name):
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
     l = [Part.make(self, pfn) for pfn in glob.glob(os.path.join(self.dirname, '*.part'))]
     l.sort(key=lambda p:p.name)
     return l

  def __iter__(self):
    return iter(self.parts)

  def part_by_fullname(self, full_name):
    try:
      return next((x for x in self.parts if x.full_name == full_name))
    except StopIteration:
      raise DataException("part not found in " + self.name + ":" + full_name)

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
      return int(y.group(1))
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
    full_name = Part.calc_full_name(name, package)
    fn = self.unique_fn(full_name)
    part = Part.make(self, fn)
    part.set_np(name, package)
    self.parts.append(part)
    return part

  def clone_part(self, to_clone_part, name, package):
    if name == '':
      raise DataException('name is not optional')
    full_name = Part.calc_full_name(name, package)
    fn = self.unique_fn(full_name)
    new_part = to_clone_part.clone(name, package, fn)
    self.parts.append(new_part)
    return new_part

class Data:

  def __init__(self, settings):
    self.cat = []
    self.dir = settings.value("basedir", os.path.join(os.environ['DATA_DIR'], default_basedir))
    if not os.path.isdir(self.dir):
      raise DataException("basedir not a directory")
    g = self.dir + '/*.cat'
    for c in glob.glob(os.path.join(self.dir, '*.cat')):
      ca = Cat(self, c)
      #print ca, ca.name
      self.cat.append(ca)
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
    c = Cat(self, ffn, name)
    self.cat.append(c)
    self.sort()
    return c

  def move_part(self, part, new_category_name):
    print "moving to", new_category_name
    old_ffn = part.ffn
    print "old_ffn", old_ffn
    new_cat = self.cat_by_name(new_category_name)
    print new_cat, new_cat.name
    new_cat.parts.append(part)
    for x in new_cat.parts:
      print x.full_name
    print "old_cat: ", part.cat.name
    part.cat.parts.remove(part)
    print "new_cat dirname", new_cat.dirname
    print "part.fn", part.fn
    new_ffn = os.path.join(new_cat.dirname, part.fn)
    print "new ffn", new_ffn
    shutil.move(old_ffn, new_ffn)
    part.cat = new_cat
    part.ffn = new_ffn
    print "moved: ", part.full_name
