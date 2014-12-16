from configparser import SafeConfigParser
import os
import sys
import requests
from datetime import datetime,  timedelta
import csv
from prettytable import PrettyTable
import collections

class ObjectS(object):

  def __init__(self, logger= None):
    self.logger = logger
    self.logger.debug("Starting base object")
    config_file = '~/samu.config'
    if os.path.isfile(os.path.expanduser('~/samu.config')):
        self.config_parse(config_file)
    else:
      self.logger.warning('No configuration file detected in home directory')
    self.cli_argument_parse()
    self.logger.debug("Samu username is: %s" % self.samu_username )
    self.logger.debug("Samu url is: %s" % self.samu_url )
    self.logger.debug("Vcenter_username is: %s" % self.vcenter_username )
    self.logger.debug("Vcenter_url is: %s" % self.vcenter_url )
  
  def config_parse(self, file):
    self.logger.info("Parsing configuration file for default values")
    self.cfg_parser = SafeConfigParser()
    self.cfg_parser.readfp(open(os.path.expanduser(file)))
    self.samu_username = self.cfg_parser.get('general', 'username')
    self.samu_password = self.cfg_parser.get('general', 'password')
    self.samu_url = self.cfg_parser.get('general', 'url')
    self.vcenter_username = self.cfg_parser.get('vmware', 'vcenter_username')
    self.vcenter_password = self.cfg_parser.get('vmware', 'vcenter_password')
    self.vcenter_url = self.cfg_parser.get('vmware', 'vcenter_url')

  def cli_argument_parse(self):
    self.logger.info("Parsing CLI arguments for global options")
    i = 0
    self.table = True
    self.csv = False
    # Default verbosity to use for logging
    self.samu_verbosity = 6
    while i < len(sys.argv):
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
      elif sys.argv[i] == '--samu_verbosity':
        self.samu_verbosity = sys.argv[i+1]
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
      if sys.argv[i] == '--table':
        self.logger.info("Table output is being used")
        self.table = True
        self.csv = False
        sys.argv.pop(i)
        i -= 1
      elif sys.argv[i] == '--csv':
        self.logger.info("Csv output is being used")
        self.table = False
        self.csv = True
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
      self.session_timestamp = token.split(splitter)[1]
    if self.session_timeframe_checker() == False:
      self.login()
    self.logger.debug("Session id is: %s" % self.sessionid)
    
  def session_timeframe_checker(self):
     timestamp = datetime.strptime(self.session_timestamp, '%Y-%m-%d %H:%M')
     now = datetime.now()
     delta =now - timestamp
     timeout = 300
     self.logger.debug("Time delta is: %s" % delta.total_seconds())
     if delta.total_seconds() < timeout:
       return True
     else:
       return False

  def login(self):
    payload = self.http_payload({'username': self.samu_username, 'password': self.samu_password})
    url = self.samu_url + "/admin/login"
    resp = requests.post(url, data=payload)
    resp = resp.json()
    self.logger.debug("Login response is: " + str(resp))
    if resp:
        self.check_status(resp)
        self.sessionid = resp['result'][0]['sessionid']
        file = open(self.sessionid_filename,  mode='w')
        now = datetime.now()
        self.session_timestamp = now.strftime("%Y-%m-%d %H:%M")
        self.logger.debug("Timestamp is: %s" % self.session_timestamp)
        file.write(self.sessionid + "====" + self.session_timestamp)
        file.close()
    else:
      self.logger.error("No response gotten from server")

  def check_status(self, resp = None):
    if resp['status'] != 'success':
      self.logger.error("Error message: %s " % resp['message'] )
      sys.exit(1)
    
  def output(self, data):
    self.logger.debug("Response is: %s" % data)
    field_names = None
    try:
      if data and data[0]:
        od = collections.OrderedDict(sorted(data[0].items()))
        field_names = list(od.keys())
        self.logger.debug("field_names is: %s" % field_names)
    except:
      self.logger.error("Could not parse response")
      exit(1)
    if self.table and field_names:
      table = PrettyTable()
      table.field_names = field_names
      table.max_width = 80
      for item in data:
        ordered_item = collections.OrderedDict(sorted(item.items()))
        self.logger.debug("Adding item to table: %s" % ordered_item)
        table.add_row(list(ordered_item.values()))
      print(table)
    if self.csv:
      writer = csv.DictWriter(sys.stdout,  delimiter=';',  fieldnames = field_names)
      writer.writeheader()
      for item in data:
        ordered_item = collections.OrderedDict(sorted(item.items()))
        writer.writerow(ordered_item)
  
  def http_payload(self, payload=None):
    if payload == None:
      payload = {'verbosity': self.samu_verbosity}
    else:
      payload['verbosity'] = self.samu_verbosity
    return payload
