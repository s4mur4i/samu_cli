from base import ObjectS
import sys
import argparse
import requests
import time

class Vmware(ObjectS):

  def __init__(self, logger = None):
    self.logger = logger
    super(Vmware, self).__init__(logger=self.logger)
    self.logger.info('Vmware module entry endpoint')

  def start(self):
    self.logger.info('Invoked starting point for Vmware')
    self.vmware_url = self.samu_url + '/vmware'
    parser = argparse.ArgumentParser( description='Samu tool for Support',  usage= ''' samu.py vmware <command> [<args>]]

Second level options are following:
  sessions
  datastore
  host
  task
  template
  ticket
  user
  folder
  resourcepool
  network
  vm

Global Options:
  -v, --verbose       increment verbosity level (max 5)
  -q, --quiet         decrease verbosity level (max 0)
  # Default verbosity level 3
  # Following options defaults to config file but can be overriden
  # with these arguments
  --samu_username     Username to use for samu
  --samu_password     Password to use for samu
  --samu_url          Url for samu Rest API
  --samu_verbosity    Verbosity level for server side
  --vcenter_username  Username to Vcenter
  --vcenter_password  Password to Vcenter
  --vcenter_url       SDK url for Vcenter

Global Output options:
  --table             Output should use Prettytable to printing
  --csv               Output should use csv format for printing (delimiter ';')
    ''')
    parser.add_argument('command',   help='Command to run')
    args = parser.parse_args(sys.argv[2:3])
    if not hasattr(self,  args.command):
      self.logger.error('Unrecognized command')
      parser.print_help()
      exit(1)
    self.payload = {}
    self.get_sessionid()
    getattr(self,  args.command)()
    
  def vm_login(self):
    url = self.vmware_url + "/-/" + self.sessionid
    payload = { 'vcenter_username': self.vcenter_username, 'vcenter_password':self.vcenter_password, 'vcenter_url':self.vcenter_url}
    resp = requests.post(url, data=self.http_payload(payload)).json()
    self.logger.debug("Response is: %s" % resp)
    self.check_status(resp)

  def check_session_exists(self):
    url = self.vmware_url + "/-/" + self.sessionid
    resp = requests.get(url, data=self.http_payload()).json()
    self.logger.debug("Session check response: %s" % resp)
    self.check_status(resp)
    for item in resp['result']:
      if (item['vcenter_username'] == self.vcenter_username and item['vcenter_url'] == self.vcenter_url):
        epoch_time = int(time.time())   
        if epoch_time - item['last_used'] > 600:
          break
        if item['active'] == 0:
          self.payload = { 'vim_id':item['id']}
        return True
      else:
        self.logger.debug("This session is not for our Vcenter and username")
    self.vm_login()

  def sessions(self):
    url = self.vmware_url + "/-/" + self.sessionid
    parser = argparse.ArgumentParser( description='Samu tool for Support',  usage= '''samu.py vmware sessions<command> [<args>]]

Sessions endpoint profile
  --active <id>
  --logout <id>

Example:
  samu.py vmware sessions
  samu.py vmware sessions --active 1
  samu.py vmware sessions --logout 1
    ''')
    parser.add_argument('--active',  default=None,  help="Change active session to id")
    parser.add_argument('--logout',  default=None,  help="Logs a session out")
    args = parser.parse_args(sys.argv[3:])
    if args.active is not None:
      self.logger.debug("Need to update active session")
      self.payload['id'] = args.active
      resp = requests.put(url, data=self.http_payload(self.payload)).json()
    elif args.logout is not None:
      self.logger.debug("Need to log session out")
      self.payload['id'] = args.logout
      resp = requests.delete(url, data=self.http_payload(self.payload)).json()
    else:
      self.logger.debug("Listing sessions")
      resp = requests.get(url, data=self.http_payload()).json()
    self.logger.debug("Response is: %s" % resp)
    self.check_status(resp)
    self.output(resp['result'])


  def vm(self):
    print "implementing"

  def network(self):
    print "implementing"

  def resourcepool(self):
    print "implementing"

  def folder(self):
    print "implementing"

  def user(self):
    print "implementing"

  def ticket(self):
    print "implementing"

  def template(self):
    print "implementing"

  def task(self):
    print "implementing"

  def host(self):
    self.check_session_exists()
    parser = argparse.ArgumentParser( description='Samu tool for Support',  usage= '''samu.py vmware host [<args>]]

Host endpoint profile
  --moref <moref>

Example:
  samu.py vmware host
  samu.py vmware host --moref 
    ''')
    parser.add_argument('--moref',  default=None,  help="Moref to Hostsystem object")
    args = parser.parse_args(sys.argv[3:])
    resp = None
    if args.moref is not None:
      url = self.vmware_url + "/host/" + args.moref + "/-/" + self.sessionid
      resp = requests.get(url, data=self.http_payload(self.payload)).json()
      connected = resp['result'][0]['vms']
      del resp['result'][0]['vms']
      self.output(connected)
      hw = resp['result'][0]['hw']
      del resp['result'][0]['hw']
      self.output([hw])
    else:
      url = self.vmware_url + "/host/-/" + self.sessionid
      resp = requests.get(url, data=self.http_payload(self.payload)).json()
    self.logger.debug("Response is: %s" % resp)
    self.check_status(resp)
    self.output(resp['result'])

  def datastore(self):
    self.check_session_exists()
    parser = argparse.ArgumentParser( description='Samu tool for Support',  usage= '''samu.py vmware datastore [<args>]]

Datastore endpoint profile
  --moref <moref>

Example:
  samu.py vmware datastore
  samu.py vmware datastore --moref datastore-111
    ''')
    parser.add_argument('--moref',  default=None,  help="Moref to datastore object")
    args = parser.parse_args(sys.argv[3:])
    resp = None
    connected = None
    if args.moref is not None:
      url = self.vmware_url + "/datastore/" + args.moref + "/-/" + self.sessionid
      resp = requests.get(url, data=self.http_payload(self.payload)).json()
      connected = resp['result'][0]['connected_vms']
      del resp['result'][0]['connected_vms']
      self.output(connected)
    else:
      url = self.vmware_url + "/datastore/-/" + self.sessionid
      resp = requests.get(url, data=self.http_payload(self.payload)).json()
    self.logger.debug("Response is: %s" % resp)
    self.check_status(resp)
    self.output(resp['result'])
