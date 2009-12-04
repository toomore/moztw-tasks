#!/usr/bin/env python
# -*- coding: utf-8 -*-
from random import choice
from datamodel import angelmasterlist

def cc(a):
  #a = ['11','22','33','44','55']
  #a = []
  #a = [i for i in range(1,10)]
  t = a[:]
  c = []

  for i in a:
    b = choice(t)
    #print t
    #print c
    if i in t:
      if len(t) ==1:
        return 'no'
        exit()
      while b == i:
        b = choice(t)
    if (b,i) in c:
        b = choice(t)
    t.remove(b)
    c.append((i,b))

  return c

def gorand(maillist,times):
  for i in range(0,times):
    a = cc (maillist)
    while a == 'no':
      a = cc(maillist)
    return a

maillist = ['toomore','tim','bob','smallfish','irvin','QQ']
qq = gorand(maillist,20)
for i,q in qq:
    angelmasterlist(key_name = i, master = q).put()
