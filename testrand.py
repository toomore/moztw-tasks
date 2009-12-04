#!/usr/bin/env python
# -*- coding: utf-8 -*-
from random import choice

def cc():
  #a = ['11','22','33','44','55']
  #a = []
  a = [i for i in range(1,9)]
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

#tt = False
'''
while cc() == 'no':
  cc()
'''
for i in range(0,20):
  a = cc ()
  while a == 'no':
    a = cc()
  print a
