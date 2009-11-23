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
  @login_required
  def get(self):
    message = mail.EmailMessage(sender = users.get_current_user().email(),
    subject="Your account has been approved")
    message.to = "Toomore bot <toomore0929@gmail.com>"
    message.body = """
Dear Albert:

Your example.com account has been approved.  You can now visit
http://www.example.com/ and sign in using your Google Account to
access new features.

Please let us know if you have any questions.

The example.com Team
    """

    message.send()

def main():
  """ Start up. """
  application = webapp.WSGIApplication([('/', first),('/mail',sendmails)],debug=True)
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
