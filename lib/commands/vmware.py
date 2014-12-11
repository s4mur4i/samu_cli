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
    if resp['status'] == 'error':
      self.vm_login()
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
    self.check_session_exists()
    parser = argparse.ArgumentParser( description='Samu tool for Support',  usage= '''samu.py vmware folder [<args>]]

Folder endpoint profile
  --moref <moref>
  --move_child_moref <moref>
  --move_child_type <VMware object type>
  --move_parent <moref>
  --create_name <folder_name>
  --delete

Example:
  samu.py vmware folder 
  samu.py vmware folder --moref group-v111

  samu.py vmware folder --create_name herring
  samu.py vmware folder --moref group-v111 --create_name herring

  samu.py vmware folder --moref group-v111 --delete

  samu.py vmware folder --move_child_moref group-v112 --move_child_type Folder 
  samu.py vmware folder --move_child_moref group-v112 --move_child_type Folder --move_parent group-v111
  samu.py vmware folder --move_child_moref group-v112 --move_child_type Folder --moref group-v111
    ''')
    parser.add_argument('--moref',  default=None,  help="Moref of folder")
    parser.add_argument('--delete',  action='store_true',  help="Delete the folder")
    parser.add_argument('--create_name',  default=None,  help="Name of folder to create")
    parser.add_argument('--move_child_moref',  default=None,  help="Child moref to move")
    parser.add_argument('--move_child_type',  default=None,  help="Type of child moref to move")
    parser.add_argument('--move_parent',  default=None,  help="Parent moref to move to")
    args = parser.parse_args(sys.argv[3:])
    resp = None
    if args.moref is not None:
      url = self.vmware_url + "/folder/" + args.moref + "/-/" + self.sessionid
      if args.create_name is not None:
        self.payload['name'] = args.create_name
        resp = requests.post(url,  data=self.http_payload(self.payload)).json()
      elif args.move_child_moref is not None:
        self.payload['child_value'] = args.move_child_moref
        self.payload['child_type'] = args.move_child_type
        resp = requests.put(url,  data=self.http_payload(self.payload)).json()
      elif args.delete == True:
        resp = requests.delete(url,  data=self.http_payload(self.payload)).json()
      else:
        resp = requests.get(url, data=self.http_payload(self.payload)).json()
    else:
      url = self.vmware_url + "/folder/-/" + self.sessionid
      if args.create_name is not None:
        self.payload['name'] = args.create_name
        resp = requests.post(url,  data=self.http_payload(self.payload)).json()
      elif args.move_child_moref is not None:
        self.payload['child_value'] = args.move_child_moref
        self.payload['child_type'] = args.move_child_type
        if args.move_parent is not None:
          self.payload['parent_value'] = args.move_parent
        resp = requests.put(url,  data=self.http_payload(self.payload)).json()
      else:
        resp = requests.get(url, data=self.http_payload(self.payload)).json()
    self.logger.debug("Response is: %s" % resp)
    self.check_status(resp)
    self.output(resp['result'])


  def user(self):
    self.check_session_exists()
    parser = argparse.ArgumentParser( description='Samu tool for Support',  usage= '''samu.py vmware user [<args>]]

User endpoint profile
  --username <username>

Example:
  samu.py vmware user 
  samu.py vmware user --username herring
    ''')
    parser.add_argument('--username',  default=None,  help="Username to query")
    args = parser.parse_args(sys.argv[3:])
    resp = None
    if args.username is not None:
      url = self.vmware_url + "/user/" + args.username + "/-/" + self.sessionid
      resp = requests.get(url, data=self.http_payload(self.payload)).json()
    else:
      url = self.vmware_url + "/user/-/" + self.sessionid
      resp = requests.get(url, data=self.http_payload(self.payload)).json()
    self.logger.debug("Response is: %s" % resp)
    self.check_status(resp)
    self.output(resp['result'])


  def ticket(self):
    self.check_session_exists()
    parser = argparse.ArgumentParser( description='Samu tool for Support',  usage= '''samu.py vmware ticket [<args>]]

Ticket endpoint profile
  --ticket <ticket_number>

Example:
  samu.py vmware ticket
  samu.py vmware ticket --ticket 1234
    ''')
    parser.add_argument('--ticket',  default=None,  help="Moref to Hostsystem object")
    args = parser.parse_args(sys.argv[3:])
    resp = None
    if args.ticket is not None:
      url = self.vmware_url + "/ticket/" + args.ticket + "/-/" + self.sessionid
      resp = requests.get(url, data=self.http_payload(self.payload)).json()
    else:
      url = self.vmware_url + "/ticket/-/" + self.sessionid
      resp = requests.get(url, data=self.http_payload(self.payload)).json()
    self.logger.debug("Response is: %s" % resp)
    self.check_status(resp)
    self.output(resp['result'])


  def template(self):
    self.check_session_exists()
    parser = argparse.ArgumentParser( description='Samu tool for Support',  usage= '''samu.py vmware template [<args>]]

Template endpoint profile
  --moref <moref>
  --unlink

Example:
  samu.py vmware template 
  samu.py vmware template --moref vm-1111
  samu.py vmware template --moref vm-1111 --unlink
    ''')
    parser.add_argument('--moref',  default=None,  help="Moref to Task object")
    parser.add_argument('--unlink',  action='store_true',  help="Unlink linked clones")
    args = parser.parse_args(sys.argv[3:])
    resp = None
    if args.moref is not None:
      url = self.vmware_url + "/template/" + args.moref + "/-/" + self.sessionid
      if args.unlink == True:
        resp = requests.delete(url, data=self.http_payload(self.payload)).json()
      else:
        resp = requests.get(url, data=self.http_payload(self.payload)).json()
        linked_clones = resp['result'][1]['active_linked_clones']
        del resp['result'][1]
        self.output(linked_clones)
    else:
      url = self.vmware_url + "/template/-/" + self.sessionid
      resp = requests.get(url, data=self.http_payload(self.payload)).json()
    self.logger.debug("Response is: %s" % resp)
    self.check_status(resp)
    self.output(resp['result'])


  def task(self):
    self.check_session_exists()
    parser = argparse.ArgumentParser( description='Samu tool for Support',  usage= '''samu.py vmware task [<args>]]

Host endpoint profile
  --moref <moref>
  --delete

Example:
  samu.py vmware task
  samu.py vmware task --moref task-1111
  samu.py vmware task --moref task-1111 --delete
    ''')
    parser.add_argument('--moref',  default=None,  help="Moref to Task object")
    parser.add_argument('--delete',  action='store_true',  help="Cancel task")
    args = parser.parse_args(sys.argv[3:])
    resp = None
    if args.moref is not None:
      url = self.vmware_url + "/task/" + args.moref + "/-/" + self.sessionid
      if args.delete == True:
        self.logger.info("Cancel task")
        resp = requests.delete(url, data=self.http_payload(self.payload)).json()
      else:
        self.logger.info("Task info requested")
        resp = requests.get(url, data=self.http_payload(self.payload)).json()
    else:
      url = self.vmware_url + "/task/-/" + self.sessionid
      resp = requests.get(url, data=self.http_payload(self.payload)).json()
    self.logger.debug("Response is: %s" % resp)
    self.check_status(resp)
    self.output(resp['result'])



  def host(self):
    self.check_session_exists()
    parser = argparse.ArgumentParser( description='Samu tool for Support',  usage= '''samu.py vmware host [<args>]]

Host endpoint profile
  --moref <moref>

Example:
  samu.py vmware host
  samu.py vmware host --moref host-11
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
