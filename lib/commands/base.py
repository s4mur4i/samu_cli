from configparser import SafeConfigParser
import os
import sys

class ObjectS(object):

  def __init__(self, logger= None):
    self.logger = logger
    self.logger.debug("Starting base object")
    config_file = '~/samu.config'
 #   if os.path.isfile(config_file):
    if os.path.isfile(os.path.expanduser('~/samu.config')):
        self.config_parse(config_file)
    else:
      self.logger.warning('No configuration file detected in home directory')
    self.cli_argument_parse()
    self.logger.debug("Samu username is: %s" % self.samu_username )
    self.logger.debug("Samu password is: %s" % self.samu_password )
    self.logger.debug("Samu url is: %s" % self.samu_url )
    self.logger.debug("Vcenter_username is: %s" % self.vcenter_username )
    self.logger.debug("Vcenter_url is: %s" % self.vcenter_url )
  
  def config_parse(self, file):
    self.cfg_parser = SafeConfigParser()
    self.cfg_parser.readfp(open(os.path.expanduser(file)))
    self.samu_username = self.cfg_parser.get('general', 'username')
    self.samu_password = self.cfg_parser.get('general', 'password')
    self.samu_url = self.cfg_parser.get('general', 'url')
    self.vcenter_username = self.cfg_parser.get('vmware', 'vcenter_username')
    self.vcenter_password = self.cfg_parser.get('vmware', 'vcenter_password')
    self.vcenter_url = self.cfg_parser.get('vmware', 'vcenter_url')

  def cli_argument_parse(self):
    for i, arg in enumerate(sys.argv):
      if arg == '--samu_username':
        self.samu_username = sys.argv[i+1]
        sys.argv[ i+1 ] = None
        sys.argv[ i ] = None
      elif arg == '--samu_password':
        self.samu_password = sys.argv[i+1]
        sys.argv[ i+1 ] = None
        sys.argv[ i ] = None
      elif arg == '--samu_url':
        self.samu_url = sys.argv[i+1]
        sys.argv[ i+1 ] = None
        sys.argv[ i ] = None
      if arg == '--vcenter_username':
        self.vcenter_username = sys.argv[i+1]
        sys.argv[ i+1 ] = None
        sys.argv[ i ] = None
      elif arg == '--vcenter_password':
        self.vcenter_password = sys.argv[i+1]
        sys.argv[ i+1 ] = None
        sys.argv[ i ] = None
      elif arg == '--vcenter_url':
        self.vcenter_url = sys.argv[i+1]
        sys.argv[ i+1 ] = None
        sys.argv[ i ] = None
    # Since we have alot of None options in sys.argv we should clean it up
    while i < len(sys.argv):
      if i >= len(sys.argv):
        break
      if sys.argv[i] == None:
        sys.argv.pop(i)
        i -= 1
      else:
        i += 1
