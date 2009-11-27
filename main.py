#!/usr/bin/env python
# -*- coding: utf-8 -*-
# app engine處理中文通用解法 http://blog.wahahajk.com/2008/08/app-engine.html

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.api import mail
from google.appengine.ext.webapp.util import login_required
from google.appengine.ext import db

from datamodel import angeldata
from angelapp import angelmenu,sendmails,showmailbox

class first(webapp.RequestHandler):
  """ index page.
  """
  def get(self):
    user = users.get_current_user()
    if user:
      greeting = ("Welcome, <b>%s</b> ! (<a href=\"%s\">sign out</a>)" % (user.nickname(), users.create_logout_url("/")))
    else:
      greeting = ("<a href=\"%s\">Sign in or register</a>." % users.create_login_url("/"))
    tv = {'login':greeting}
    self.response.out.write(template.render('./template/h_index.htm',{'tv':tv}))

class sendmailss(webapp.RequestHandler):
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
        tip = '飛來飛去小天使<br>找來找去小主人'
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
          'login': "Welcome, <b>%s</b> ! (<a href=\"%s\">sign out</a>)" % (user.nickname(), users.create_logout_url("/mail"))}
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

class mailtomaster(webapp.RequestHandler):
  @login_required
  def get(self):
    user = users.get_current_user()
    table = """
<form action="/mailtomaster" method="POST">
傳送給小主人<br>
<textarea name="note" cols="25" rows="7"></textarea><br>
<input type="submit" value="傳送">
</form>
"""
    tv = {'tip': table,
          'menu': angelmenu(user.email()).listmenu(),
          'login': "Welcome, <b>%s</b> ! (<a href=\"%s\">sign out</a>)" % (user.nickname(), users.create_logout_url("/mail"))}
    self.response.out.write(template.render('./template/h_index.htm',{'tv':tv}))

  def post(self):
    user = users.get_current_user()
    if user.email():
      pass
    else:
      self.redirect('/mail')
    table = self.request.get('note')
    sendmails(user.email()).sendmails(table,angel='1')
    tip = """
傳送完畢！<br>
%s<br>
<br>
<a href="/mail">確定！</a> 或 <a href="/mailtomaster">再傳一封</a>
""" % str(table.replace('\r\n','<br>').encode('utf-8'))
    tv = {'tip': tip,
          'menu': angelmenu(user.email()).listmenu(),
          'login': "Welcome, <b>%s</b> ! (<a href=\"%s\">sign out</a>)" % (user.nickname(), users.create_logout_url("/mail"))}
    self.response.out.write(template.render('./template/h_index.htm',{'tv':tv}))

class mailtoangel(webapp.RequestHandler):
  @login_required
  def get(self):
    user = users.get_current_user()
    table = """
<form action="/mailtoangel" method="POST">
感謝我的小天使<br>
<textarea name="note" cols="25" rows="7"></textarea><br>
<input type="submit" value="謝謝小天使！">
</form>
"""
    tv = {'tip': table,
          'menu': angelmenu(user.email()).listmenu(),
          'login': "Welcome, <b>%s</b> ! (<a href=\"%s\">sign out</a>)" % (user.nickname(), users.create_logout_url("/mail"))}
    self.response.out.write(template.render('./template/h_index.htm',{'tv':tv}))

  def post(self):
    user = users.get_current_user()
    if user.email():
      pass
    else:
      self.redirect('/mail')
    table = self.request.get('note')
    ## send mail
    #try:
    sendmails(user.email()).sendmails(table,master='1')
    #except:
    #  self.redirect('/mail')
    tip = """
傳送完畢！<br>
%s<br>
<br>
<a href="/mail">確定！</a> 或 <a href="/mailtoangel">再次感謝！</a>
""" % str(table.replace('\r\n','<br>').encode('utf-8'))
    tv = {'tip': tip,
          'menu': angelmenu(user.email()).listmenu(),
          'login': "Welcome, <b>%s</b> ! (<a href=\"%s\">sign out</a>)" % (user.nickname(), users.create_logout_url("/mail"))}
    self.response.out.write(template.render('./template/h_index.htm',{'tv':tv}))

class mailbox(webapp.RequestHandler):
  @login_required
  def get(self):
    user = users.get_current_user()
    a = showmailbox(user.email())

    tv = {'tip': '<table class="mailbox">' + a.show() + '</table>',
          'menu': angelmenu(user.email()).listmenu(),
          'login': "Welcome, <b>%s</b> ! (<a href=\"%s\">sign out</a>)" % (user.nickname(), users.create_logout_url("/mail"))}
    self.response.out.write(template.render('./template/h_index.htm',{'tv':tv}))

def main():
  """ Start up. """
  application = webapp.WSGIApplication([('/', angelgame),
                                        ('/mail',angelgame),
                                        ('/mailtomaster',mailtomaster),
                                        ('/mailtoangel',mailtoangel),
                                        ('/mailbox',mailbox)
                                        ],debug=True)
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
