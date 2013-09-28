#!/usr/bin/env python
#
# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import os, os.path, copy, shutil
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
    self.fn = os.path.basename(fn)
    self.ffn = os.path.join(self.cat.dirname, self.fn)
    self.c = Config()
    self.vl = []
    self.bl = []
    self.tl = []
    self.tags = []
    if os.path.exists(self.ffn):
      self.__read_config()
    self.__set_tags()

  def clone(self, name, package, fn):
    new_part = Part(self.cat, fn)
    new_part.name = name
    new_part.package = package
    new_part.full_name = Part.full_name(name, package)
    new_part.full_name_bak = new_part.full_name
    new_part.fn = fn
    new_part.ffn = os.path.join(new_part.cat.dirname, fn)
    new_part.vl = copy.deepcopy(self.vl)
    new_part.bl = copy.deepcopy(self.bl)
    new_part.tl = copy.deepcopy(self.tl)
    new_part.location = copy.deepcopy(self.location)
    new_part.footprint = copy.deepcopy(self.footprint)
    new_part.single_value = copy.deepcopy(self.single_value)
    new_part.quantity = copy.deepcopy(self.quantity)
    new_part.threshold = copy.deepcopy(self.threshold)
    new_part.c.add_section('main')
    new_part.c.add_section('values')
    new_part.c.add_section('buy')
    new_part.c.add_section('tag')
    new_part.c.set('main', 'name', name)
    new_part.c.set('main', 'package', package)
    return new_part

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
    self.__set_tags()

  def __read_config(self):
    if self.c.read(self.ffn) == []:
      raise DataException('file not found ' + self.ffn)
    self.name = self.c.get('main', 'name')
    self.package = self.c.get('main', 'package')
    print "read package:", self.name, self.package
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
      #print (k,v)
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
      #print (k,v)
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
    self.__set_tags()
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

  def match(self, txt):
    for x in self.tags:
      if txt in x:
        return True
    return False

  def __set_tags(self):
    self.tags = []
    self.tags.append(self.full_name.lower())
    for (k,v) in self.tl:
      if k != "":
        self.tags.append(k.lower())
      if v != "":
        self.tags.append(v.lower())

class Cat:

  def __init__(self, data, dirname, name=None):
    self.data = data
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

  def clone_part(self, to_clone_part, name, package):
    if name == '':
      raise DataException('name is not optional')
    full_name = Part.full_name(name, package)
    fn = self.unique_fn(full_name)
    new_part = to_clone_part.clone(name, package, fn)
    self.parts.append(new_part)
    return new_part

class Data:

  def __init__(self, settings):
    self.cat = []
    self.dir = settings.value("basedir", default_basedir)
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
