#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datamodel import angeldata

class angelmenu:
  def __init__(self,angel):
    self.angel = angel
    self.master = angeldata.get_by_key_name(angel).mymaster

  def mastermenu(self):
    if self.master:
      a = '<a href="/mailtomaster">關心小主人</a>'
    else:
      a = '沒有建立小主人'
    return a

  def myangel(self):
    an = angeldata.gql("WHERE mymaster = '%s'" % self.angel)
       
    if int(an.count()):
      #a = '<a href="/mailtoangel">呼叫小天使 %s </a>' % str(an.get().key().id_or_name())
      a = '<a href="/mailtoangel">呼叫小天使</a>'
    else:
      a = '哭哭！沒有小天使！'
    
    return a

  def listmenu(self):
    a = self.mastermenu() + " " + self.myangel()
    return a
