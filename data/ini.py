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

class Part:

  def __init__(self, cat, fn):
    self.cat = cat
    self.name = ""
    self.fn = os.path.basename(fn)
    self.ffn = os.path.join(self.cat.dirname, self.fn)
    self.c = Config()
    self.vl = [] # value list
    self.bl = [] # buy list
    self.tl = [] # tag list
    self.tags = []
    self.last_changed = "unknown"
    if os.path.exists(self.ffn):
      self.__read_config()

  def __repr__(self):
    return "Part(%s,%s,%s)" % (self.cat.name, self.name, self.fn)

  def clone(self, name, package, fn):
    new_part = Part(self.cat, fn)
    new_part.name = name
    new_part.package = package
    new_part.fn = fn
    new_part.ffn = os.path.join(new_part.cat.dirname, fn)
    new_part.vl = copy.deepcopy(self.vl)
    new_part.bl = copy.deepcopy(self.bl)
    new_part.tl = copy.deepcopy(self.tl)
    new_part.location = copy.deepcopy(self.location)
    new_part.footprint = copy.deepcopy(self.footprint)
    new_part.single_value = copy.deepcopy(self.single_value) # TODO single value is implied from one value in value list
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
