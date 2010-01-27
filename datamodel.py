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

class ActionEV(db.Model):
  """ Action data """
  created_at = db.DateTimeProperty(auto_now_add = True)
  updated_at = db.DateTimeProperty(auto_now_add = True)
  actname = db.StringProperty()
  actdate = db.DateTimeProperty()
  actlocation = db.PostalAddressProperty()
  actdesc = db.TextProperty()
  acttag = db.ListProperty(str)
  actuser = db.ReferenceProperty(Volunteer)

class ActionRegUser(db.Model):
  """ Action register """
  created_at = db.DateTimeProperty(auto_now_add = True)
  updated_at = db.DateTimeProperty(auto_now_add = True)
  actionreguser = db.ReferenceProperty(Volunteer)
  actionreguserStr = db.StringProperty()
  actionreg = db.ReferenceProperty(ActionEV)
  actionregStr = db.StringProperty()

class UserUniId(db.Model):
  """ User uni id. key_name is uni id."""
  created_at = db.DateTimeProperty(auto_now_add = True)
  userVStr = db.StringProperty()
  userV = db.ReferenceProperty(Volunteer)
