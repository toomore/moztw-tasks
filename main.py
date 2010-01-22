#!/usr/bin/env python
# -*- coding: utf-8 -*-
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from headerapp import Renderer

class first(webapp.RequestHandler):
  """ start up
  """
  def get(self):
    otv = {'title': 'Index'}
    a = Renderer()
    a.render(self,'./template/htm_index.htm',otv)

def main():
  """ Start up. """
  application = webapp.WSGIApplication([('/', first)],debug=True)
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
