#!/usr/bin/env python
# -*- coding: utf-8 -*-
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.api import mail
from google.appengine.ext.webapp.util import login_required
from google.appengine.ext import db

from datamodel import angeldata
from angelapp import angelmenu

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

class angelgame(webapp.RequestHandler):
  @login_required
  def get(self):
    user = users.get_current_user()
    if angeldata.get_by_key_name(user.email()):
        tip = 'user:' + user.email()
        if angeldata.get_by_key_name(user.email()).mymaster is None:
          buildmaster = '''
小主人的 Mail 尚未建立!
<form action="/mail" method="POST">
<input name="mymastermail">
<input type="submit" value="建立">
</form>
<br>打錯就沒有小主人喔！
'''
          tip = buildmaster
    else:
        tip = '檔案建立，請記得建立小主人資料！<br><a href="/mail">是的是的！我會乖乖的建立</a>'
        angeldata(key_name = unicode(user.email())).put()
    tv = {'tip': tip,
          'menu': angelmenu(user.email()).listmenu(),
          'login': "Welcome, %s! (<a href=\"%s\">sign out</a>)" % (user.nickname(), users.create_logout_url("/mail"))}
    self.response.out.write(template.render('./template/h_index.htm',{'tv':tv}))
  def post(self):
    user = users.get_current_user()
    try:    
      mm = self.request.get('mymastermail')
      u = angeldata.get_by_key_name(user.email())
      u.mymaster = db.Email(mm)
      u.put()
    except:
      pass
    self.redirect('/mail')

def main():
  """ Start up. """
  application = webapp.WSGIApplication([('/', first),('/mail',angelgame)],debug=True)
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
