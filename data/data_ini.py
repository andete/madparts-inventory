#!/usr/bin/env python
#
# (c) 2014 Joost Yervante Damad <joost@damad.be>
# License: GPL

import os, os.path, datetime
import ConfigParser, StringIO

# we don't want the interpolation feature
class Config(ConfigParser.RawConfigParser):
  pass

# with default
def wd(d, f):
  try:
    return f()
  except ConfigParser.NoOptionError:
    return d

class Part(object):

  def __init__(self, dirname, fn):
    self.name = ""
    self.dirname = dirname
    self.fn = os.path.basename(fn)
    self.ffn = os.path.join(self.dirname, self.fn)
    self.c = Config()
    self.value = []
    self.buy = []
    self.tag = []
    self.last_changed = "unknown"
    if os.path.exists(self.ffn):
      self.__read_config()

  def save_new(self, name_package):
    (name, package) = name_package
    self.name = name
    self.package = package
    self.c.add_section('main')
    self.c.add_section('values')
    self.c.add_section('buy')
    self.c.add_section('tag')
    self.c.set('main', 'name', self.name)
    self.c.set('main', 'package', self.package)
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
    datetimev = datetime.datetime.fromtimestamp(os.stat(self.ffn).st_mtime)
    self.last_changed = datetimev.strftime("%Y-%m-%d %a %H:%M:%S")
    self.name = self.c.get('main', 'name')
    self.package = self.c.get('main', 'package')
    #print "read package:", self.name, self.package
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
        self.value.append((t[0],t[1],t[2]))
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
        self.buy.append((t[0],t[1],t[2],t[3],t[4]))
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
        self.tag.append((t[0],t[1]))

  def save(self):
    print 'saving', self.name
    self.c.set('main', 'name', self.name)
    self.c.set('main', 'location', self.location)
    self.c.set('main', 'footprint', self.footprint)
    self.c.set('main', 'single-value', str(self.single_value))
    self.c.set('main', 'quantity', self.quantity)
    self.c.set('main', 'threshold', self.threshold)
    self.c.remove_section('values')
    self.c.add_section('values')
    for i in range(0, len(self.value)):
      self.c.set('values', "%03d_value" % (i), self.value[i][0])
      self.c.set('values', "%03d_quantity" % (i), self.value[i][1])
      self.c.set('values', "%03d_threshold" % (i), self.value[i][2])
    self.c.remove_section('buy')
    self.c.add_section('buy')
    for i in range(0, len(self.buy)):
      self.c.set('buy', "%03d_when" % (i), self.buy[i][0])
      self.c.set('buy', "%03d_where" % (i), self.buy[i][1])
      self.c.set('buy', "%03d_id" % (i), self.buy[i][2])
      self.c.set('buy', "%03d_price" % (i), self.buy[i][3])
      self.c.set('buy', "%03d_amount" % (i), self.buy[i][4])
    self.c.remove_section('tag')
    self.c.add_section('tag')
    for i in range(0, len(self.tag)):
      self.c.set('tag', "%03d_tag" % (i), self.tag[i][0])
      self.c.set('tag', "%03d_value" % (i), self.tag[i][1])
    output = StringIO.StringIO()
    orig = ""
    try:
      with open(self.ffn, 'r') as f:
        orig = f.read()
    except IOError:
      pass
    self.c.write(output)
    if output.getvalue() != orig:
      print "file changed, writing"
      with open(self.ffn, 'w+') as f:
        self.c.write(f)
      datetimev = datetime.datetime.fromtimestamp(os.stat(self.ffn).st_mtime)
      self.last_changed = datetimev.strftime("%Y-%m-%d %a %H:%M:%S")
    else:
      print "no change, no write"

  def save_to_json(self):
    import data_json
    data_json.Part.save_part(self)

class Cat(object):

  def __init__(self, dirname, name=None):
    self.dirname = dirname
    self.file = os.path.join(self.dirname, 'cat.ini')
    self.c = Config()
    self.prop = {}
    if name is not None:
      self.__make(name)
    else:
      self.__load()

  def __make(self, name):
    if os.path.exists(self.dirname):
      raise DataException("category already exists")
    self.c.add_section('main')
    self.c.set('main', 'name', name)
    os.mkdir(self.dirname)
    with open(self.file, 'w+') as f:
      self.c.write(f)
    self.name = name
  
  def __load(self):
    self.c.read(self.file)
    self.name = self.c.get('main', 'name')
    if self.c.has_section('properties'):
      for (k,v) in self.c.items('properties'):
        self.prop[k] = v
