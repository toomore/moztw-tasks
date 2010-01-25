#!/usr/bin/env python
# -*- coding: utf-8 -*-
from google.appengine.ext.webapp import template
from google.appengine.api import users
import datetime

class Renderer:
  def render(self,header,tempfile,orgvalue):
    user = users.get_current_user()
    if user:
      greeting = ("<b>%s</b> setting (<a href=\"%s\">sign out</a>) " % (user.nickname(), users.create_logout_url("/")))
    else:
      greeting = ("<a href=\"%s\">Sign in or register</a>. " % users.create_login_url("/"))

    if user:
      menu = "→ 事件｜活動"
    else:
      menu = ''

    tv = {
      'login': greeting + str(datetime.datetime.now() + datetime.timedelta(hours=8))[:-7],
      'menu': menu
    }
    tv.update(orgvalue)
    header.response.out.write(template.render(tempfile,tv))
