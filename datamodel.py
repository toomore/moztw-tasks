#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Data property. """

from google.appengine.ext import db

class Volunteer(db.Model):
  """ Volunteer basedata. """
  created_at = db.DateTimeProperty(auto_now_add = True)
  updated_at = db.DateTimeProperty(auto_now_add = True)
  nickname = db.StringProperty()
  userid = db.StringProperty()
  location = db.StringProperty()
  profile = db.StringProperty()

class angelmasterlist(db.Model):
  master = db.EmailProperty()

class angeldata(db.Model):
  """ User data. """
  mymaster = db.EmailProperty()
  nickname = db.StringProperty()
  refs = db.ReferenceProperty(angelmasterlist,collection_name = 'emails')
  created_at = db.DateTimeProperty(auto_now_add = True)

class angelmailbox(db.Model):
  """ sendtype 1:god 2:to master 3:to angel"""
  sendtype = db.IntegerProperty()
  sended = db.BooleanProperty()
  sender = db.EmailProperty()
  to = db.EmailProperty()
  context = db.TextProperty()
  created_at = db.DateTimeProperty(auto_now_add = True)

class guessangel(db.Model):
  ggangel = db.EmailProperty()
  ref = db.ReferenceProperty(angeldata,collection_name = 'ggg') #ref angeldata.user(angel).key
  created_at = db.DateTimeProperty(auto_now_add = True)
