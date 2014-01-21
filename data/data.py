#!/usr/bin/env python
#
# (c) 2013-2014 Joost Yervante Damad <joost@damad.be>
# License: GPL

import os, os.path, copy, shutil, re
import glob, datetime
import data_ini, data_json

default_basedir = "example"

class DataException(Exception):
  pass

# part proxy
class Part(object):
  
  def __init__(self, cat):
    self.cat = cat

  @staticmethod
  def make(cat, fn, name_package = None):
    part = Part(cat)
    try:
      part.p = data_json.Part(cat.dirname, fn)
    except data_json.NotJsonError:
      part.p = data_ini.Part(cat.dirname, fn)
    if not name_package is None:
      part.p.save_new(name_package)
    part.__set_tags()
    part.full_name_bak = part.full_name
    return part

  def __repr__(self):
    return "Part(%s,%s,%s)" % (self.cat.name, self.name, self.fn)

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
    new_part.p = data_json.Part(self.cat.dirname, fn)
    new_part.name = name
    new_part.value[:] = copy.deepcopy(self.value)
    new_part.buy[:] = copy.deepcopy(self.buy)
    new_part.tag[:] = copy.deepcopy(self.tag)
    new_part.location = copy.deepcopy(self.location)
    new_part.footprint = copy.deepcopy(self.footprint)
    new_part.single_value = copy.deepcopy(self.single_value)
    new_part.package = package
    # TODO: just save
    new_part.p.save_new((name, package))
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

  @property
  def value(self):
     return self.p.value
 
  @value.setter
  def value(self, value):
     self.p.value = value

  @property
  def buy(self):
     return self.p.buy

  @property
  def tag(self):
     return self.p.tag

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
    for (k,v) in self.tag:
      if k != "":
        self.tags.append(k.lower())
      if v != "":
        self.tags.append(v.lower())

  def match(self, txt):
    for x in self.tags:
      if txt in x:
        return True
    return False


class Cat(object):

  def __init__(self, data):
    self.data = data

  @staticmethod
  def make(data, dirname, name=None):
    cat = Cat(data)
    cat.p = data_ini.Cat(dirname, name)
    cat.parts = cat.__scan_parts()
    return cat

  def __repr__(self):
    return "Cat(%s,%s)" % (self.name, self.dirname)

  @property
  def name(self):
    return self.p.name

  @property
  def prop(self):
    return self.p.prop

  @property
  def dirname(self):
    return self.p.dirname

  @property
  def file(self):
    return self.p.file

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
    part = Part.make(self, fn, (name, package))
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
      self.cat.append(Cat.make(self, c))
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
    c = Cat.make(self, ffn, name)
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
