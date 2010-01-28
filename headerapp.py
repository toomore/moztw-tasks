#!/usr/bin/env python
# -*- coding: utf-8 -*-
from google.appengine.ext.webapp import template
from google.appengine.api import users
import datetime
from utilapp import register

class Renderer:
  def render(self,header,tempfile,orgvalue):
    user = users.get_current_user()

    if user:
      if not register(user.email()).is_reg: ## check user if writed user info.
        if header.request.path == '/userinfo':
          pass
        else:
          header.redirect('/userinfo')
        #print '123'
        #print dir(header)
        #print 

      greeting = (
        "<img class='mimg' src='/images/user.png'> <b>%s</b> <img class='mimg' src='/images/vcard_edit.png'>設定 <a href=\"%s\"><img class='mimg' src='/images/user_go.png'>登出</a> " % 
          (
            user.nickname(), users.create_logout_url(header.request.path)
          )
      )
    else:
      greeting = ("<a href=\"%s\"><img class='mimg' src='/images/door_in.png'>登入</a> " % users.create_login_url(header.request.path))

    if user:
      menu = "→ <img class='mimg' src='/images/lightning.png'>事件 <a href='/action'><img class='mimg' src='/images/calendar.png'>活動</a>"
    else:
      menu = ''

    tv = {
      'login': greeting + str(datetime.datetime.now() + datetime.timedelta(hours=8))[:-7],
      'menu': menu
    }
    tv.update(orgvalue)
    header.response.out.write(template.render(tempfile,tv))
