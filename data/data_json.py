#!/usr/bin/env python
#
# (c) 2014 Joost Yervante Damad <joost@damad.be>
# License: GPL

import os, os.path, datetime
import json, StringIO

class NotJsonError(Exception):
  pass

class Part(object):

  def __init__(self, dirname, fn):
    self.name = ""
    self.dirname = dirname
    self.fn = os.path.basename(fn)
    self.ffn = os.path.join(self.dirname, self.fn)
    self.location = ''
    self.footprint = ''
    self.single_value = True
    self.quantity = ''
    self.threshold = ''
    self.value = [] # value list
    self.buy = [] # buy list
    self.tag = [] # tag list
    self.last_changed = "unknown"
    if os.path.exists(self.ffn):
      try:
        self.__read_json()
      except ValueError:
        raise NotJsonError

  def __read_json(self):
    j = None
    with open(self.ffn) as f:
      j = json.load(f)
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
    for (k,v) in j['tag'].items():
      # TODO keep dict
      self.tag.append((k,v))

  def save_new(self, (name, package)):
    return self.save()

  @staticmethod
  def save_part(part):
    print 'saving', part.name
    j = {}
    def set_to_json(name, default=''):
      j[name] = getattr(part, name, default)
    for x in ['name', 'location', 'footprint', 'quantity', 'threshold']:
       set_to_json(x)
    set_to_json('single_value', True)

    j['values'] = []
    for (v,q,t) in part.value:
      d = {}
      d['value'] = v
      d['quantity'] = q
      d['threshold'] = t
      j['values'].append(d)

    j['buy'] = []
    for (w1,w2,i,p,a) in part.buy:
      d = {}
      d['when'] = w1
      d['where'] = w2
      d['id'] = i
      d['price'] = p
      d['amount'] = p
      j['buy'].append(d)

    j['tag'] = {}
    for (k,v) in part.tag:
      j['tag'][k] = v
    orig = ""
    try:
      with open(part.ffn, 'r') as f:
        orig = json.load(f)
    except IOError:
      pass
    except ValueError:
      pass
    output = StringIO.StringIO()
    json.dump(j, output, indent=2)
    if output.getvalue() != orig:
      print "file changed, writing"
      with open(part.ffn, 'w+') as f:
        json.dump(j, f, indent=2)
      datetimev = datetime.datetime.fromtimestamp(os.stat(part.ffn).st_mtime)
      part.last_changed = datetimev.strftime("%Y-%m-%d %a %H:%M:%S")
    else:
      print "no change, no write"

  def save(self):
    Part.save_part(self)
