from base import ObjectS
import sys

class Admin(ObjectS):

  def __init__(self, logger = None):
    self.logger = logger
    super(Admin, self).__init__(logger=self.logger)
    self.logger.info('Admin module entry endpoint')

  def start(self):
    self.logger.info('Invoked starting point for Admin')
