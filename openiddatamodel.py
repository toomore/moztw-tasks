#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib
from google.appengine.ext import db

############## Models ###################
class Person(db.Model):
  openid = db.StringProperty()
  date = db.DateTimeProperty(auto_now_add=True)
  hashedkey = db.StringProperty()

  def pretty_openid(self):
    return self.openid.replace('http://','').replace('https://','').rstrip('/').split('#')[0]

  def put(self):
    if self.hashedkey is None:
      if self.is_saved():
        key = self.key()
      else:
        key = db.Model.put(self)

      self.hashedkey = hashlib.sha1(str(key)).hexdigest()

    assert self.hashedkey
    return db.Model.put(self)

class Session(db.Expando):
  # the logged in person
  person = db.ReferenceProperty(Person)

  # OpenID library session stuff
  openid_stuff = db.TextProperty()

  # when someone tries to demand a site and they aren't logged in,
  # we store it here
  url = db.StringProperty()

  # this goes in the cookie
  session_id = db.StringProperty()

  def put(self):
    if self.session_id is None:

      if self.is_saved():
        key = self.key() 
      else:
        key = db.Expando.put(self)

      self.session_id = hashlib.sha1(str(key)).hexdigest()
    else:
      key = self.key()

    assert self.session_id
    db.Expando.put(self)
    return key
