#!/usr/bin/env python
# -*- coding: utf-8 -*-
from google.appengine.api import users
from google.appengine.ext.webapp.util import login_required
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

import datetime
from headerapp import Renderer
from datamodel import Volunteer

class first(webapp.RequestHandler):
  """ index """
  def get(self):
    otv = {'title': '歡迎自投羅網'}
    a = Renderer()
    a.render(self,'./template/htm_index.htm',otv)

class action_page(webapp.RequestHandler):
  """ action """
  @login_required
  def get(self):
    otv = {'title': '參加活動'}
    a = Renderer()
    a.render(self,'./template/htm_action.htm',otv)

class action_add(webapp.RequestHandler):
  """ action add """
  @login_required
  def get(self):
    otv = {
            'title': '新增活動',
            'deftime': str(datetime.datetime.now() + datetime.timedelta(hours=8))[:-10]}
    a = Renderer()
    a.render(self,'./template/htm_action_add.htm',otv)

  def post(self):
    user = users.get_current_user()
    userkey = Volunteer.get_by_key_name(user.email())
    print '123'
    print userkey.key()

class userinfo(webapp.RequestHandler):
  """ create user info when first login. """
  @login_required
  def get(self):
    otv = {'title': '建立基本資料'}
    a = Renderer()
    a.render(self,'./template/htm_userinfo.htm',otv)

  def post(self):
    user = users.get_current_user()

    if self.request.get('nickname') and self.request.get('id'):
      Volunteer(key_name = user.email(),
                nickname = self.request.get('nickname'),
                userid = self.request.get('id')).put()

    self.redirect('/')

class errorpage(webapp.RequestHandler):
  """ Error page """
  def get(self):
    otv = {'title': '錯誤頁面'}
    a = Renderer()
    a.render(self,'./template/htm_error.htm',otv)

def main():
  """ Start up. """
  application = webapp.WSGIApplication([
                              ('/', first),
                              ('/action', action_page),
                              ('/action/add', action_add),
                              ('/userinfo', userinfo),
                              ('/.*', errorpage)
                              ],debug=True)
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
