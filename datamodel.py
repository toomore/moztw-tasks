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
