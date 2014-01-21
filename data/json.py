#!/usr/bin/env python
#
# (c) 2014 Joost Yervante Damad <joost@damad.be>
# License: GPL

import os, os.path. json

class Part(object):

  def __init__(self, dirname, fn):
    self.name = ""
    self.dirname = dirname
    self.fn = os.path.basename(fn)
    self.ffn = os.path.join(self.dirname, self.fn)
    self.value = [] # value list
    self.buy = [] # buy list
    self.tag = [] # tag list
    self.last_changed = "unknown"
    if os.path.exists(self.ffn):
      self.__read_json()

  def __read_config(self):
    j = None
    with open(self.ffn) as f:
      j = json.read(f)
    datetimev = datetime.datetime.fromtimestamp(os.stat(self.ffn).st_mtime)
    self.last_changed = datetimev.strftime("%Y-%m-%d %a %H:%M:%S")
    def set_from_json(name, default=''):
      setattr(self, name, default)
      if name in j:
        setattr(self, name, j[name])
    for x in ['name', 'package', 'location','footprint', 'quantity', 'threshold']:
      set_from_json(x)
    set_from_json('single_value', True)
    for x in j['values']:
      # TODO keep dict
      self.value.append((x['value'], x['quantity'], x['threshold']))
    for x in j['buy']:
      # TODO keep dict
      self.buy.append((x['when'], x['where'], x['id'], x['price'], x['amount']))
    for (k,v) in j['tag'].items:
      # TODO keep dict
      self.tag.append((k,v))

  def save(self):
    print 'saving', self.name
    j = {}
    def set_to_json(name, default=''):
      j['name'] = getattr(self, name, default)
    for x in ['name', 'location', 'footprint', 'quantity', 'threshold']:
       set_to_json(x)
    set_to_json('single_value', True)

    j['values'] = []
    for (v,q,t) in self.value:
      d = {}
      d['value'] = v
      d['quantity'] = q
      d['threshold'] = t
      j['values'].append(d)

    j['buy'] = []
    for (w1,w2,i,p,a) in self.buy:
      d = {}
      d['when'] = w1
      d['where'] = w2
      d['id'] = i
      d['price'] = p
      d['amount'] = p
      j['buy'].append(d)

    j['tag'] = {}
    for (k,v) in self.tag:
    j['tag'][k] = v

    output = StringIO.StringIO()
    orig = ""
    try:
      with open(self.ffn, 'r') as f:
        orig = json.read(f)
    except IOError:
      pass
    json.write(output)
    if output.getvalue() != orig:
      print "file changed, writing"
      with open(self.ffn, 'w+') as f:
        json.write(f)
      datetimev = datetime.datetime.fromtimestamp(os.stat(self.ffn).st_mtime)
      self.last_changed = datetimev.strftime("%Y-%m-%d %a %H:%M:%S")
    else:
      print "no change, no write"
