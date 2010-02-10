#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cgi
import wsgiref.handlers
import urlparse, urllib
import os
import logging
import datetime
import time
import Cookie
import pprint
import pickle
import hashlib

from google.appengine.api import users
from google.appengine.ext.webapp.util import login_required
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from openid import fetchers
from openid.consumer.consumer import Consumer
from openid.consumer import discover
from fetcher import UrlfetchFetcher
import store

from headerapp import Renderer
from datamodel import Volunteer,ActionEV,ActionRegUser,UserUniId

_DEBUG = False

############## Models ###################
class Person(db.Model):
  openid = db.StringProperty()
  date = db.DateTimeProperty(auto_now_add=True)
  hashedkey = db.StringProperty()

  def pretty_openid(self):
    return self.openid.replace('http://','').replace('https://','').rstrip('/').split('#')[0]

  def put(self):
    if self.hashedkey is None:
      if self.is_saved():
        key = self.key()
      else:
        key = db.Model.put(self)

      self.hashedkey = hashlib.sha1(str(key)).hexdigest()

    assert self.hashedkey
    return db.Model.put(self)

class Session(db.Expando):
  # the logged in person
  person = db.ReferenceProperty(Person)

  # OpenID library session stuff
  openid_stuff = db.TextProperty()

  # when someone tries to demand a site and they aren't logged in,
  # we store it here
  url = db.StringProperty()

  # this goes in the cookie
  session_id = db.StringProperty()

  def put(self):
    if self.session_id is None:

      if self.is_saved():
        key = self.key() 
      else:
        key = db.Expando.put(self)

      self.session_id = hashlib.sha1(str(key)).hexdigest()
    else:
      key = self.key()

    assert self.session_id
    db.Expando.put(self)
    return key

############# Base Handler ##############
class BaseHandler(webapp.RequestHandler):
  session = None
  logged_in_person = None

  def get_store(self):
    return store.DatastoreStore()

  def args_to_dict(self):
    req = self.request
    return dict([(arg, req.get(arg)) for arg in req.arguments()])

  def has_session(self):
    return bool(self.session)

  def get_session_id_from_cookie(self):
    if self.request.headers.has_key('Cookie'):
      cookie = Cookie.SimpleCookie(self.request.headers['Cookie'])

      if cookie.has_key('session_id'):
        return cookie['session_id'].value

    return None

  def write_session_id_cookie(self, session_id):
    expires = datetime.datetime.now() + datetime.timedelta(weeks=2)
    expires_rfc822 = expires.strftime('%a, %d %b %Y %H:%M:%S +0000')
    self.response.headers.add_header(
      'Set-Cookie', 'session_id=%s; path=/; expires=%s' % (str(session_id), expires_rfc822))

  def get_session(self, create=True):
    if self.session:
      return self.session

    # get existing session
    session_id = self.get_session_id_from_cookie()
    if session_id:
      sessions = Session.gql("WHERE session_id = :1", session_id)
      if sessions.count() == 1:
        self.session = sessions[0]
        return self.session

    if create:
      self.session = Session()
      self.session.put()
      self.write_session_id_cookie(self.session.session_id)
      return self.session

    return None

  def get_logged_in_person(self):
    if self.logged_in_person:
      return self.logged_in_person

    s = self.get_session(create=False)
    if s and s.person:
      self.logged_in_person = s.person
      return self.logged_in_person

    return None

  def render(self, template_name, extra_values={}):
    values = {
      'request': self.request,
      'debug': self.request.get('deb'),
      'lip': self.get_logged_in_person()
      }
    '''
    if values['lip']:
      values['bookmarklet'] = bookmarklet(self.request.host, values['lip'])
    else:
      values['bookmarklet'] = None
    '''
    values.update(extra_values)
    cwd = os.path.dirname(__file__)
    path = os.path.join(cwd, 'template', template_name + '.htm')
    logging.debug(path)
    self.response.out.write(template.render(path, values, debug=_DEBUG))

  def report_error(self, message):
    """Shows an error HTML page.

    Args:
    message: string
    A detailed error message.
    """
    args = pprint.pformat(self.args_to_dict())
    self.render('error', vars())
    logging.error(message)

  def show_main_page(self, error_msg=None):
    """Do an internal (non-302) redirect to the front page.
    Preserves the user agent's requested URL.
    """
    page = errorpage()
    page.request = self.request
    page.response = self.response
    page.get(error_msg)

############## Page Models ###################
class first(BaseHandler):
  """ index """
  def get(self):
    lip = self.get_logged_in_person()
    template_values = {
      'title': '歡迎自投羅網',
      'bug': dir(lip)
    }

    self.response.headers['X-XRDS-Location'] = 'http://'+self.request.host+'/rpxrds'
    self.render('htm_index', template_values)

class action_page(webapp.RequestHandler):
  """ action """
  #@login_required
  def get(self):
    act = ActionEV.all().order('-actdate')
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
          #could_edit = '<a href="/act/%s/edit">編輯活動</a>' % actno
          could_edit = 1

      ActRegUser = ActionRegUser.gql("where actionregStr = '%s'" % aev.key())
      join_user = []
      for i in ActRegUser:
        o = {
          'nickname':i.actionreguser.nickname,
          'uniid':i.actionreguser.useruniid_set.fetch(1)[0].key().id_or_name(),
        }
        join_user.append(o)

      otv = {
        'title': aev.actname,
        'sidetitle': '',
        'actno': actno,
        'actname': aev.actname,
        'actdate': str(aev.actdate)[:-3],
        'actlocation': aev.actlocation,
        'actdesc': aev.actdesc.replace('\r\n','<br>'),
        'actuser': '<a href="/user/%s">%s <img class="mimg" src="/images/vcard.png"></a>' % (
          aev.actuser.useruniid_set.fetch(1)[0].key().id_or_name(), aev.actuser.nickname),
        'join_no': ActRegUser.count(),
        'join_user': join_user,
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
        #print '123'
        #print ActionRegUser.gql("where actionregStr = '%s'" % aev.key()).count()
        #print dir(ARU.get())
        self.redirect('/act/%s' % aev.key().id())
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
    user = users.get_current_user()
    if user:
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
    else:
      self.redirect('/')

class errorpage(BaseHandler):
  """ Error page """
  def get(self, error_msg=None):
    otv = {
            'title': '錯誤頁面',
            'error_msg': error_msg
          }
    self.render('htm_error', otv)

############## OpenID Models ###################
class LoginPage(BaseHandler):
  def get(self):
    template_values = {'title': '登入'}
    self.render('htm_login', template_values)

class OpenIDStartSubmit(BaseHandler):
  def post(self):
    openid = self.request.get('openid_identifier')
    if not openid:
      self.show_main_page()
      return

    c = Consumer({},self.get_store())
    try:
      auth_request = c.begin(openid)
    except discover.DiscoveryFailure, e:
      logging.error('Error with begin on '+openid)
      logging.error(str(e))
      self.show_main_page('An error occured determining your server information.  Please try again.')
      return

    parts = list(urlparse.urlparse(self.request.uri))
    parts[2] = 'openid-finish'
    parts[4] = ''
    parts[5] = ''
    return_to = urlparse.urlunparse(parts)

    realm = urlparse.urlunparse(parts[0:2] + [''] * 4)

    # save the session stuff
    session = self.get_session()
    session.openid_stuff = pickle.dumps(c.session)
    session.put()

    # send the redirect!  we use a meta because appengine bombs out
    # sometimes with long redirect urls
    redirect_url = auth_request.redirectURL(realm, return_to)
    self.response.out.write("<html><head><meta http-equiv=\"refresh\" content=\"0;url=%s\"></head><body></body></html>" % (redirect_url,))

class OpenIDFinish(BaseHandler):
  def get(self):
    args = self.args_to_dict()
    url = 'http://'+self.request.host+'/openid-finish'

    session = self.get_session()
    s = {}
    if session.openid_stuff:
      try:
        s = pickle.loads(str(session.openid_stuff))
      except:
        session.openid_stuff = None

    session.put()

    c = Consumer(s, self.get_store())
    auth_response = c.complete(args, url)

    if auth_response.status == 'success':
      openid = auth_response.getDisplayIdentifier()
      persons = Person.gql('WHERE openid = :1', openid)
      if persons.count() == 0:
        p = Person()
        p.openid = openid
        p.put()
      else:
        p = persons[0]

      s = self.get_session()
      s.person = p.key()
      self.logged_in_person = p

      if s.url:
        add = AddWebsiteSubmit()
        add.request = self.request
        add.response = self.response
        add.vote_for(s.url, p)
        s.url = None

      s.put()

      self.redirect('/home')

    else:
      self.show_main_page('OpenID verification failed :(')

class LogoutSubmit(BaseHandler):
  def get(self):
    s = self.get_session()
    if s:
      s.person = None
      s.put()

    self.redirect('/')

class RelyingPartyXRDS(BaseHandler):
  def get(self):
    xrds = """
<?xml version='1.0' encoding='UTF-8'?>
<xrds:XRDS
  xmlns:xrds='xri://$xrds'
  xmlns:openid='http://openid.net/xmlns/1.0'
  xmlns='xri://$xrd*($v*2.0)'>
  <XRD>
    <Service>
      <Type>http://specs.openid.net/auth/2.0/return_to</Type>
      <URI>http://%s/openid-finish</URI>
    </Service>
</XRD>
</xrds:XRDS>
""" % (self.request.host,)

    self.response.headers['Content-Type'] = 'application/xrds+xml'
    self.response.out.write(xrds)

############## main Models ###################
def main():
  """ Start up. """
  application = webapp.WSGIApplication(
                                      [
                                        ('/', first),
                                        ('/login', LoginPage),
                                        ('/logout', LogoutSubmit),
                                        ('/openid-start', OpenIDStartSubmit),
                                        ('/openid-finish', OpenIDFinish),
                                        ('/rpxrds', RelyingPartyXRDS)
#                                        ('/action', action_page),
 #                                       ('/action/add', action_add),
  #                                      ('/act/(\d+)', action_read),
   #                                     ('/act/(\d+)/edit', action_edit),
    #                                    ('/act/(\d+)/join', action_join),
     #                                   ('/userinfo', userinfo),
      #                                  ('/user/(\w+)', user_page),
       #                                 ('/.*', errorpage)
                                      ],debug=True)
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
