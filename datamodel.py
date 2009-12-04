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

class angeldata(db.Model):

  mymaster = db.EmailProperty()
  created_at = db.DateTimeProperty(auto_now_add = True)

class angelmailbox(db.Model):
  """ sendtype 1:god 2:to master 3:to angel"""
  sendtype = db.IntegerProperty()
  sended = db.BooleanProperty()
  sender = db.EmailProperty()
  to = db.EmailProperty()
  context = db.TextProperty()
  created_at = db.DateTimeProperty(auto_now_add = True)

class angelandmaster(db.Model):
  user = db.EmailProperty()
  master = db.EmailProperty()

class refname(db.Model):
  user = db.EmailProperty()

class reftest(db.Model):
  refone = db.ReferenceProperty(angeldata,collection_name = 'eee')
  created_at = db.DateTimeProperty(auto_now_add = True)
