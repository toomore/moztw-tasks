#!/usr/bin/env python
# -*- coding: utf-8 -*-
from google.appengine.api import users
from google.appengine.ext.webapp.util import login_required
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

import datetime,time
from headerapp import Renderer
from datamodel import Volunteer,ActionEV,ActionRegUser,UserUniId

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
    act = ActionEV.all()
    act_d = []

    for i in act:
      act_d.append(
        {
          'id': i.key().id(),
          'actname': i.actname,
          'actdate': str(i.actdate)[:-3]
        }
      )

    otv = {'title': '參加活動','act': act_d}

    a = Renderer()
    a.render(self,'./template/htm_action.htm',otv)

class action_add(webapp.RequestHandler):
  """ action add """
  @login_required
  def get(self):
    otv = {
      'title': '新增活動',
      'sidetitle': '新增活動',
      'deftime': str(datetime.datetime.now() + datetime.timedelta(hours=8))[:-10]
    }
    a = Renderer()
    a.render(self,'./template/htm_action_add.htm',otv)

  def post(self):
    user = users.get_current_user()

    if user: ## login or not
      ## Get user key for action user ref.
      userkey = Volunteer.get_by_key_name(user.email())
      ## convert str to date
      try:
        ft = time.strptime(self.request.get('actime'), '%Y-%m-%d %H:%M')
        ## create a new action
        aev = ActionEV(
          actname = self.request.get('acname'),
          actdate = datetime.datetime(ft.tm_year,ft.tm_mon,ft.tm_mday,ft.tm_hour,ft.tm_min),
          actlocation = self.request.get('aclocation'),
          actdesc = self.request.get('actdes'),
          actuser = userkey.key()
        ).put()
        ## Go to the action page
        self.redirect('/act/%s' % aev.id())
      except:
        self.redirect('/action/add')
    else:
      ## wrong user
      self.redirect('/')

class action_read(webapp.RequestHandler):
  """ action read """
  def get(self,actno):
    user = users.get_current_user()
    aev = ActionEV().get_by_id(int(actno))
    could_edit = ''

    if aev:
      if user:
        if user.email() == aev.actuser.key().id_or_name():
          could_edit = '<a href="/act/%s/edit">編輯活動</a>' % actno

      otv = {
        'title': aev.actname,
        'sidetitle': '',
        'actno': actno,
        'actname': aev.actname,
        'actdate': str(aev.actdate)[:-3],
        'actlocation': aev.actlocation,
        'actdesc': aev.actdesc.replace('\r\n','<br>'),
        'actuser': '<a href="/user/%s">%s</a>' % (
          aev.actuser.useruniid_set.fetch(1)[0].key().id_or_name(), aev.actuser.nickname),
        'could_edit': could_edit,
        'debug': aev.actuser.useruniid_set.fetch(1)[0].key().id_or_name()
      }
      a = Renderer()
      a.render(self,'./template/htm_action_read.htm',otv)
    else:
      self.redirect('/error')

class action_edit(webapp.RequestHandler):
  """ action edit """
  def get(self,actno):
    user = users.get_current_user()
    aev = ActionEV().get_by_id(int(actno))
    
    if user: ## login or not
      if user.email() == aev.actuser.key().id_or_name():
        ## correct user
        if aev:
          otv = {
            'title': aev.actname,
            'sidetitle': '編輯活動',
            'actname': aev.actname,
            'deftime': str(aev.actdate)[:-3],
            'actlocation': aev.actlocation,
            'actdesc': aev.actdesc,
            'actuser': aev.actuser.nickname,
            'edit_cancel': '<a href="/act/%s">取消編輯</a>' % actno,
            'debug': aev.actuser.key().id_or_name()
          }
          a = Renderer()
          a.render(self,'./template/htm_action_add.htm',otv)
      else:
        ## wrong user
        self.redirect('/')
    else:
      ## not login
      self.redirect('/')

  def post(self,actno):
    aev = ActionEV().get_by_id(int(actno))
    user = users.get_current_user()

    if user: ## login or not
      if user.email() == aev.actuser.key().id_or_name():
        ## correct user
        ## convert str to date
        try:
          ft = time.strptime(self.request.get('actime'), '%Y-%m-%d %H:%M')
          ## change the value
          aev.actname = self.request.get('acname')
          aev.actdate = datetime.datetime(ft.tm_year,ft.tm_mon,ft.tm_mday,ft.tm_hour,ft.tm_min)
          aev.actlocation = self.request.get('aclocation')
          aev.actdesc = self.request.get('actdes')
          ## into data.
          aev.put()
          ## Go to action page.
          self.redirect('/act/%s' % actno)
        except:
          self.redirect('/act/%s/edit' % actno)
      else:
        ## wrong user
        self.redirect('/')
    else:
      ## not login
      self.redirect('/')

class action_join(webapp.RequestHandler):
  """ action edit """
  def post(self,actno):
    aev = ActionEV().get_by_id(int(actno))
    user = users.get_current_user()

    if aev and user: ## action and user is existed and login.
      userV = Volunteer.get_by_key_name(user.email())
      
      ARU = ActionRegUser.gql(
        "where actionregStr = '%s' and actionreguserStr = '%s'" % 
        (
          aev.key(),
          Volunteer.get_by_key_name(user.email()).key()
        )
      )
      #ARU = ActionRegUser.all()
      #ARU.filter('actionreg=', aev.get())
      #ARU.filter('actionreguser=',Volunteer.get_by_key_name(user.email()).key())
      if ARU.count():
        ## Join
        print '123'
        print ActionRegUser.gql("where actionregStr = '%s'" % aev.key()).count()
        print dir(ARU.get())
      else:
        ## unJoin
        regact = ActionRegUser(
          actionreguser = userV,
          actionreguserStr = str(userV.key()),
          actionreg = aev,
          actionregStr = str(aev.key())
        ).put()
        if regact:
          ## RegOK Go to action page.
          self.redirect('/act/%s' % aev.key().id())
        else:
          ## RegError
          self.redirect('/')
    else:
      ## wrong action and user login.
      self.redirect('/')

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
      try:
        import re
        ## verify the id
        cid = re.search(re.compile('[\w]+'), self.request.get('id')).group().lower()
      except:
        self.redirect('/userinfo')

      idused = UserUniId.get_by_key_name(cid)
      if idused:
        ## used.
        self.redirect('/userinfo')
      else:
        ## unused
        user_key = Volunteer(
          key_name = user.email(),
          nickname = self.request.get('nickname'),
          userid = cid
        ).put()

        UserUniId(
          key_name = str(cid),
          userVStr = str(user_key),
          userV = user_key
        ).put()
        self.redirect('/user/%s' % cid)

class user_page(webapp.RequestHandler):
  """ create user info when first login. """
  @login_required
  def get(self,userid):
    userpage = UserUniId.get_by_key_name(userid)
    if userpage:
      otv = {
        'title': userpage.userV.nickname,
        'nickname': userpage.userV.nickname
      }
      a = Renderer()
      a.render(self,'./template/htm_user_page.htm',otv)
    else:
      self.redirect('/error') 

class errorpage(webapp.RequestHandler):
  """ Error page """
  def get(self):
    otv = {'title': '錯誤頁面'}
    a = Renderer()
    a.render(self,'./template/htm_error.htm',otv)

def main():
  """ Start up. """
  application = webapp.WSGIApplication(
                                      [
                                        ('/', first),
                                        ('/action', action_page),
                                        ('/action/add', action_add),
                                        ('/act/(\d+)', action_read),
                                        ('/act/(\d+)/edit', action_edit),
                                        ('/act/(\d+)/join', action_join),
                                        ('/userinfo', userinfo),
                                        ('/user/(\w+)', user_page),
                                        ('/.*', errorpage)
                                      ],debug=True)
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
