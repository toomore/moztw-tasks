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

import datetime

from datamodel import angeldata,angelmasterlist,guessangel
from angelapp import angelmenu,sendmails,showmailbox,sendalluser,angelmailbox,guesstheangel

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
      tip = '飛來飛去小天使<br>找來找去小主人<br><br>In <b>%s</b><br>遊戲就要結束了！' % str(datetime.datetime(2009,12,26) - datetime.datetime.now() + datetime.timedelta(hours=16))[:-7]
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
      if angeldata.get_by_key_name(user.email()).nickname is None:
        buildmaster = '''
設定暱稱
<form action="/mail" method="POST">
<input name="mynickname">
<input type="submit" value="設定">
</form><br>這會顯示在所有參與人員名單上，但不會有任何的提示關於你的小主人。
'''
        tip = buildmaster
    else:
      tip = '檔案建立，請記得關心小主人喔！<br><a href="/mail">是的是的！我會乖乖的關心小主人</a>'
      ## Need to get the master info.
      try:
        getusermaster = angelmasterlist.get_by_key_name(user.email())
        angeldata(key_name = unicode(user.email()),
                  mymaster = getusermaster.master
                  #refs = getusermaster.key()
                  ).put()
      except:
        tip = '<img src="http://upload.wikimedia.org/wikipedia/commons/thumb/6/65/Lucas_Cranach_d._Ä._035.jpg/300px-Lucas_Cranach_d._Ä._035.jpg"><br><br>You are out of the <a href="http://en.wikipedia.org/wiki/Garden_of_Eden">Eden</a>...'
    try:
      tv = {'tip': tip,
            'menu': angelmenu(user.email()).listmenu(),
            'login': "Welcome, <b>%s</b> ! (<a href=\"%s\">sign out</a>)" % (user.nickname(), users.create_logout_url("/mail"))}
    except:
      tv = {'tip': tip,
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
      mm = self.request.get('mynickname')
      u = angeldata.get_by_key_name(user.email())
      u.nickname = mm
      u.put()
    self.redirect('/mail')

class mailtomaster(webapp.RequestHandler):
  @login_required
  def get(self):
    user = users.get_current_user()
    mymaster = ((angelmasterlist.get_by_key_name(user.email()).master).encode('utf-8'))
    try:
      mymasternickname = angeldata.get_by_key_name(mymaster).nickname
      if mymasternickname is None:
        pass
      else:
        mymasternickname = mymasternickname
    except:
      mymasternickname = '<i>沒有設定暱稱</i>'

    table = """
<form action="/mailtomaster" method="POST">
傳送給小主人<br>
我的小主人是 <font color="#99aa99"><b>%s</b> <i>(%s)</i></font><br>
<textarea name="note" cols="25" rows="7"></textarea><br>
<input type="submit" value="傳送"><br>
%s
</form>
""".decode('utf-8') % (mymasternickname,mymaster.split('@')[0],guesstheangel(user.email()).guess)

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
%s<br>
<textarea name="note" cols="25" rows="7"></textarea><br>
<input type="submit" value="謝謝小天使！">
</form>
""".decode('utf-8') % guesstheangel(user.email()).whatiguess
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

class mailsetting(webapp.RequestHandler):
  @login_required
  def get(self):
    user = users.get_current_user()
    nickname = angeldata.get_by_key_name(user.email()).nickname
    if nickname is None:
      nickname = ''
    else:
      nicaname = nickname.encode('utf-8')
    buildmaster = '''
設定暱稱
<form action="/mail" method="POST">
<input name="mynickname" value="%s">
<input type="submit" value="設定">
</form><br>這會顯示在所有參與人員名單上，但不會有任何的提示關於你的小主人。
''' % nickname.encode('utf-8')
#''' % (angeldata.get_by_key_name(user.email()).nickname).encode('utf-8')

    tip = buildmaster
    tv = {'tip': tip,
          'menu': angelmenu(user.email()).listmenu(),
          'login': "Welcome, <b>%s</b> ! (<a href=\"%s\">sign out</a>)" % (user.nickname(), users.create_logout_url("/mail"))}
    self.response.out.write(template.render('./template/h_index.htm',{'tv':tv}))

class mailtoall(webapp.RequestHandler):
  @login_required
  def get(self):
    user = users.get_current_user()
    table = """
<form action="/mailtoall" method="POST">
傳送給所有人<br>
<textarea name="note" cols="25" rows="7"></textarea><br>
<input type="submit" value="通知">
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
    #sendmails(user.email()).sendmails(table,angel='1')
    #sendalluser().allmail
    footnote = """
--
這是一封由雷鳥郵差代發的信件，回覆給郵差是沒有用的啦！
我是 God！不要懷疑！多多關心小主人！多多感謝小天使！
才能得永生！
http://moztw-tasks.appspot.com/mail
"""

    message = mail.EmailMessage(
      sender = 'MozTW 雷鳥郵差 <noreply@moztw-tasks.appspotmail.com>',
      subject="您有一封 God 寄來的通知！")
    message.bcc = sendalluser().allmail
    message.body = "這是一封 God 寄給您的信，通知重要的內容：\r\n\r\n%s %s" % (table.encode('utf-8'),footnote)
    #message.send()
    for i in sendalluser().allmail:
      intoangelmailbox = angelmailbox(sender = 'God',
                                      to = i,
                                      context = table,
                                      sendtype = 1,
                                      sended = bool(0)).put()

    tip = """
通知完畢！<br>
%s<br>
<br>
<a href="/mail">確定！</a> 或 <a href="/mailtoall">再通知一封</a>
""" % str(table.replace('\r\n','<br>').encode('utf-8'))
    tv = {'tip': tip,
          'menu': angelmenu(user.email()).listmenu(),
          'login': "Welcome, <b>%s</b> ! (<a href=\"%s\">sign out</a>)" % (user.nickname(), users.create_logout_url("/mail"))}
    self.response.out.write(template.render('./template/h_index.htm',{'tv':tv}))

class reftest(webapp.RequestHandler):
  @login_required
  def get(self):
    user = users.get_current_user()
    d = angeldata.get_by_key_name(user.email())
    tv = {'tip': [(str((i,str(getattr(d.refs.angeldata_set,i))))+'<br>') for i in dir(d.refs.angeldata_set)]}

class chart(webapp.RequestHandler):
  @login_required
  def get(self):
    user = users.get_current_user()
    a = angelmailbox
    fromgod = a.all().filter('sendtype =',1).count()
    fromangel = a.all().filter('sendtype =',2).count()
    frommaster = a.all().filter('sendtype =',3).count()
    loginnum = angeldata.all().count()
    allpeople = angelmasterlist.all().count()
    tip = "G: %s, A: %s, M: %s<br>Login People: %s/%s" % (fromgod,fromangel,frommaster,loginnum,allpeople)
    img = 'http://chart.apis.google.com/chart?chs=400x100&cht=bhs&chd=t:%s,%s,%s&chxt=x,y&chxl=1:|M|A|G' % (fromgod,fromangel,frommaster)
    tv = {'tip': tip + '<br><img src="%s">' % img,
          'menu': angelmenu(user.email()).listmenu(),
          'login': "Welcome, <b>%s</b> ! (<a href=\"%s\">sign out</a>)" % (user.nickname(), users.create_logout_url("/mail"))}
    self.response.out.write(template.render('./template/h_index.htm',{'tv':tv}))

class angelguess(webapp.RequestHandler):
  @login_required
  def get(self):
    user = users.get_current_user()
    #print '123'
    #guesstheangel().userkeys(user.email())
    #k = angeldata.get_by_key_name(user.email())
    #guessangel(ggangel = 'q@gmail.com', ref = k.key()).put()
    #print dir(guesstheangel)
    u = angeldata.all()
    tip = []
    r = ''
    tr = ''
    for i in u:
      #print i.key().id_or_name()
      #i.nickname,i.key()
      if i.key().id_or_name() == user.email():
        pass
      else:
        r = r + '<tr><td><input id="%s" name="gangel" type="radio" value="%s"></td><td><label for="%s"><b>%s</b> <font color="#aabbaa"><i>(%s)</i></font></label></td></tr>' % ((i.key().id_or_name()).split('@')[0],i.key(),(i.key().id_or_name()).split('@')[0],i.nickname,(i.key().id_or_name()).split('@')[0])
        tr = '<div><form method="POST">我覺得我的小天使是？<table class="ggangel">%s</table>可以三心兩意，想到就猜！<br><input type="submit" value="Go"></form></div>'.decode('utf-8') % r

    tv = {'tip': tr,
          'menu': angelmenu(user.email()).listmenu(),
          'login': "Welcome, <b>%s</b> ! (<a href=\"%s\">sign out</a>)" % (user.nickname(), users.create_logout_url("/mail"))}
    self.response.out.write(template.render('./template/h_index.htm',{'tv':tv}))

  def post(self):
    user = users.get_current_user()
    u = angeldata.get(self.request.get('gangel'))

    guesstheangel(user.email()).indata(u.key().id_or_name())
    tip = '''
%s<br><br>
<a href="/mailtoangel">問問看</a>是不是真的！
'''.decode('utf-8') % guesstheangel(user.email()).whatiguess
    tv = {'tip': tip,
          'menu': angelmenu(user.email()).listmenu(),
          'login': "Welcome, <b>%s</b> ! (<a href=\"%s\">sign out</a>)" % (user.nickname(), users.create_logout_url("/mail"))}
    self.response.out.write(template.render('./template/h_index.htm',{'tv':tv}))

def main():
  """ Start up. """
  application = webapp.WSGIApplication([('/', angelgame),
                                        ('/mail',angelgame),
                                        ('/mailtomaster',mailtomaster),
                                        ('/mailtoangel',mailtoangel),
                                        ('/mailtoall',mailtoall),
                                        ('/mailbox',mailbox),
                                        ('/mailsetting',mailsetting),
                                        ('/angelguess',angelguess),
                                        ('/reftest',reftest),
                                        ('/chart',chart)
                                        ],debug=True)
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
