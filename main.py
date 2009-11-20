#!/usr/bin/env python
# -*- coding: utf-8 -*-
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from datamodel import Volunteer

class first(webapp.RequestHandler):
  """ Clean/reset memcache
  """
  def get(self):
    user = users.get_current_user()
    if user:
      greeting = ("Welcome, %s! (<a href=\"%s\">sign out</a>)" % (user.nickname(), users.create_logout_url("/")))
    else:
      greeting = ("<a href=\"%s\">Sign in or register</a>." % users.create_login_url("/"))

    self.response.out.write(greeting)

def main():
  """ Start up. """
  application = webapp.WSGIApplication([('/', first)],debug=True)
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
