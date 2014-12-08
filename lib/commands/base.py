from configparser import SafeConfigParser
import os
import sys
import requests
from datetime import datetime,  timedelta

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
    self.get_sessionid()
  
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
    i = 0
    while i < len(sys.argv):
    #for i, arg in enumerate(sys.argv):
      if i >= len(sys.argv):
        break
      if sys.argv[i] == '--samu_username':
        self.samu_username = sys.argv[i+1]
        sys.argv.pop(i+1)
        sys.argv.pop(i)
        i -= 1
      elif sys.argv[i] == '--samu_password':
        self.samu_password = sys.argv[i+1]
        sys.argv.pop(i+1)
        sys.argv.pop(i)
        i -= 1
      elif sys.argv[i] == '--samu_url':
        self.samu_url = sys.argv[i+1]
        sys.argv.pop(i+1)
        sys.argv.pop(i)
        i -= 1
      if sys.argv[i] == '--vcenter_username':
        self.vcenter_username = sys.argv[i+1]
        sys.argv.pop(i+1)
        sys.argv.pop(i)
        i -= 1
      elif sys.argv[i] == '--vcenter_password':
        self.vcenter_password = sys.argv[i+1]
        sys.argv.pop(i+1)
        sys.argv.pop(i)
        i -= 1
      elif sys.argv[i] == '--vcenter_url':
        self.vcenter_url = sys.argv[i+1]
        sys.argv.pop(i+1)
        sys.argv.pop(i)
        i -= 1
      else:
        i += 1

  def get_sessionid(self):
    self.sessionid_filename = "/tmp/%s_samu_session" % self.samu_username
    self.logger.debug("Session ID file: %s" % self.sessionid_filename)
    self.sessionid = None
    try:
      file = open(self.sessionid_filename)
    except IOError:
      self.login()
    if self.sessionid is None:
      token = file.read()
      splitter = "===="
      self.sessionid = token.split(splitter)[0]
    self.logger.debug("Session id is: %s" % self.sessionid)
    

  def login(self):
    payload = {'username': self.samu_username, 'password': self.samu_password}
    url = self.samu_url + "/admin/login"
    resp = requests.post(url, data=payload)
    resp = resp.json()
    self.logger.debug("Response received: " + str(resp))
    if resp:
        if resp['status'] != 'success':
          self.logger.error("Error message: %s " % resp['message'] )
          sys.exit(1)
        self.sessionid = resp['result'][0]['sessionid']
        file = open(self.sessionid_filename,  mode='w')
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%m")
        file.write(self.sessionid + "====" + timestamp)
        file.close()
    else:
      self.logger.error("No response gotten from server")
