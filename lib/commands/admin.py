from base import ObjectS
import sys

class Admin(ObjectS):

  def __init__(self):
    print 'Admin module entry endpoint'

  def start(self):
    print 'Invoked starting point for Admin'
