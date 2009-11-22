#!/usr/bin/env python
# -*- coding: utf-8 -*-
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.api import mail
from google.appengine.ext.webapp.util import login_required

from datamodel import Volunteer

class first(webapp.RequestHandler):
  """ index page.
  """
  def get(self):
    user = users.get_current_user()
    if user:
      greeting = ("Welcome, %s! (<a href=\"%s\">sign out</a>)" % (user.nickname(), users.create_logout_url("/")))
    else:
      greeting = ("<a href=\"%s\">Sign in or register</a>." % users.create_login_url("/"))
    tv = {'login':greeting}
    self.response.out.write(template.render('./template/h_index.htm',{'tv':tv}))

class sendmails(webapp.RequestHandler):
  #@login_required
  def post(self):
    to_addr = 'toomore0929@gmail.com'

    message = mail.EmailMessage()
    message.sender = users.get_current_user().email()
    message.to = to_addr
    message.body = """
I've invited you to Example.com!

To accept this invitation, click the following link,
or copy and paste the URL into your browser's address
bar:

%s
    """ % users.get_current_user().email()

    message.send()

def main():
  """ Start up. """
  application = webapp.WSGIApplication([('/', first),('/mail',sendmails)],debug=True)
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
