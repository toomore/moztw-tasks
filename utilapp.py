#!/usr/bin/env python
# -*- coding: utf-8 -*-

class register:
  def __init__(self,user):
    from datamodel import Volunteer
    self._data = Volunteer()
    self._user = user

  @property
  def is_reg(self):
    if self._data.get_by_key_name(self._user):
      return True
    else:
      return False
