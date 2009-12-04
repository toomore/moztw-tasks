#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datamodel import reftest,angeldata
s = angeldata.get_by_key_name('toomore0929@gmail.com')

d = reftest(refone=s)
d.put()
print '123'
