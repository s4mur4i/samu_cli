from base import ObjectS
import sys
import argparse
import requests
import time

class Vmware(ObjectS):

  def __init__(self, logger = None, global_options = None):
    self.logger = logger
    self.global_options = global_options
    super(Vmware, self).__init__(logger=self.logger)
    self.logger.info('Vmware module entry endpoint')

  def start(self):
    self.logger.info('Invoked starting point for Vmware')
    self.vmware_url = self.samu_url + '/vmware'
    parser = argparse.ArgumentParser( description='Samu tool for Support',  usage= '''samu.py vmware <command> [<args>]]

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
  networks
  dvp
  switch
  hostnetwork
  vm_info
  vm
    ''' + self.global_options)
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
    self.logger.debug("Login response is: %s" % resp)
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
        if epoch_time - int(item['last_used']) > 600:
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
    ''' + self.global_options)
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
    self.check_status(resp)
    self.output(resp['result'])

  def vm_info(self):
    self.check_session_exists()
    parser = argparse.ArgumentParser( description='Samu tool for Support',  usage= '''samu.py vmware vm_info [<args>]

Vm_info endpoint
    --moref <moref>

Example:
  samu.py vmware vm_info
  samu.py vmware vm_info --moref vm-111
    ''' + self.global_options)
    parser.add_argument('--moref',  default=None,  help="Moref to a vm object")
    args = parser.parse_args(sys.argv[3:])
    resp = None
    if args.moref is not None:
      url = self.vmware_url + "/vm/" + args.moref + "/-/" + self.sessionid
      resp = requests.get(url, data=self.http_payload(self.payload)).json()
    else:
      url = self.vmware_url + "/vm/-/" + self.sessionid
      resp = requests.get(url, data=self.http_payload(self.payload)).json()
    self.check_status(resp)
    self.output(resp['result'])

  def vm(self):
    self.check_session_exists()
    parser = argparse.ArgumentParser( description='Samu tool for Support',  usage= '''samu.py vmware vm [<args>]

Vm endpoint
    --moref <moref>
    --delete
    --change <value>
    --clone
    --ticket <number>
    --parent_folder <moref>
    --altername <name>
    --numcpus <number>
    --memorymb <size>
    --cdrom
    --disk
    --interface
    --powerstatus
    --snapshot
    --event
    --process
    --annotation
    --transfer
    --cpu
    --memory
    --id <id>
    --type <poewrstate type>
    --filter <filter type>
    --name <name>
    --dest <filename>
    --source <filename>
    --username <password>
    --password <password>
    --overwrite
    --size <filesize>
    --memorymb <size in mb>
    --numcpus <int>
    --create
    --remove
    --desc <description>
    --active

Example:
  samu.py vmware vm --moref vm-111
  samu.py vmware vm --moref vm-111 --delete
  samu.py vmware vm --moref vm-111 --clone --ticket 1234 --parent_folder group-111 --altername client --numcpus 4 --memorymb 4096

  samu.py vmware vm --moref vm-111 --event
  samu.py vmware vm --moref vm-111 --event --filter VmPoweredOnEvent
  
  samu.py vmware vm --moref vm-111 --process
  samu.py vmware vm --moref vm-111 --process --workdir 'C:/' --prog 'C:/windows/System32/dsget.exe' --prog_arg '/? > C:/tmp.log' --env 'TEST=Test'

  samu.py vmware vm --moref vm-111 --cpu
  samu.py vmware vm --moref vm-111 --cpu --numcpus 4
  
  samu.py vmware vm --moref vm-111 --memory
  samu.py vmware vm --moref vm-111 --memory --memorymb 1000

  samu.py vmware vm --moref vm-111 --powerstatus
  samu.py vmware vm --moref vm-111 --powerstatus --type reboot

  samu.py vmware vm --moref vm-111 --event 
  samu.py vmware vm --moref vm-111 --event --filter VmPoweredOnEvent 
  
  samu.py vmware vm --moref vm-111 --cdrom
  samu.py vmware vm --moref vm-111 --cdrom --create
  samu.py vmware vm --moref vm-111 --cdrom --id 0
  samu.py vmware vm --moref vm-111 --cdrom --id 0 --change_cdrom --iso '[Datastore] path/to/iso.iso'
  samu.py vmware vm --moref vm-111 --cdrom --id 0 --remove
  samu.py vmware vm --moref vm-111 --disk
  samu.py vmware vm --moref vm-111 --disk --create --size 10
  samu.py vmware vm --moref vm-111 --disk --id 0
  samu.py vmware vm --moref vm-111 --disk --id 0 --remove
  samu.py vmware vm --moref vm-111 --interface
  samu.py vmware vm --moref vm-111 --interface --create
  samu.py vmware vm --moref vm-111 --interface --id 0
  samu.py vmware vm --moref vm-111 --interface --id 0 --remove
  samu.py vmware vm --moref vm-111 --snapshot
  samu.py vmware vm --moref vm-111 --snapshot --create
  samu.py vmware vm --moref vm-111 --snapshot --remove
  samu.py vmware vm --moref vm-111 --snapshot --id 111
  samu.py vmware vm --moref vm-111 --snapshot --id 111 --active
  samu.py vmware vm --moref vm-111 --snapshot --id 111 --remove

  samu.py vmware vm --moref vm-111 --annotation
  samu.py vmware vm --moref vm-111 --annotation --name samu_password
  samu.py vmware vm --moref vm-111 --annotation --name samu_password --change test
  samu.py vmware vm --moref vm-111 --annotation --name samu_password --delete_annotation
  
  samu.py vmware vm --moref vm-111 --transfer --source 'c:/test.log' 
  samu.py vmware vm --moref vm-111 --transfer --dest 'c:/test.log' --size 111 --overwrite 1
    ''' + self.global_options)
    parser.add_argument('--moref',  default=None,  help="Moref to a vm object")
    parser.add_argument('--delete',  action='store_true',  help="VM should be deleted")
    parser.add_argument('--delete_annotation',  action='store_true',  help="Annotation should be deleted")
    parser.add_argument('--clone',  action='store_true',  help="Linked clone should be created from vm")
    parser.add_argument('--ticket',  default=None,  help="Ticket number for environment")
    parser.add_argument('--parent_folder',  default=None,  help="Parent folder that should be destination, by default linked_clone folder is used")
    parser.add_argument('--altername',  default=None,  help="Alternate name for machine")
    parser.add_argument('--numcpus',  default=None,  help="Number of CPUs to use for machine")
    parser.add_argument('--memorymb',  default=None,  help="Size of memory")
    parser.add_argument('--id',  default=None,  help="Id of the endpoint")
    parser.add_argument('--desc',  default=None,  help="Description")
    parser.add_argument('--type',  default=None,  help="State of powerstatus to move to")
    parser.add_argument('--filter',  default=None,  help="Type of filter to use for events")
    parser.add_argument('--name',  default=None,  help="Name of annotation to query")
    parser.add_argument('--username',  default=None,  help="Username for login to vm")
    parser.add_argument('--size',  default=None,  help="Size of upload file")
    parser.add_argument('--password',  default=None,  help="Password for login to vm")
    parser.add_argument('--dest',  default=None,  help="Destination file to upload to")
    parser.add_argument('--source',  default=None,  help="Source file to download")
    parser.add_argument('--workdir',  default=None,  help="Workdir to use for program")
    parser.add_argument('--prog',  default=None,  help="Program to run")
    parser.add_argument('--env',  default=None,  help="Envronment variables for program")
    parser.add_argument('--iso',  default=None,  help="Change cdrom to iso")
    parser.add_argument('--prog_arg',  default=None,  help="Arguments to program to run")
    parser.add_argument('--change',  default=None,  help="Change some value to new")
    parser.add_argument('--change_cdrom', action='store_true',  help="Change cdrom to an iso or back to host backing")
    parser.add_argument('--cdrom',  action='store_true',  help="Cdrom management")
    parser.add_argument('--active',  action='store_true',  help="Snapshot should become active")
    parser.add_argument('--disk',  action='store_true',  help="Disk management")
    parser.add_argument('--interface',  action='store_true',  help="Interface management")
    parser.add_argument('--powerstatus',  action='store_true',  help="Power management")
    parser.add_argument('--snapshot',  action='store_true',  help="Snapshot management")
    parser.add_argument('--event',  action='store_true',  help="Event management")
    parser.add_argument('--process',  action='store_true',  help="Process management")
    parser.add_argument('--annotation',  action='store_true',  help="Annotation management")
    parser.add_argument('--transfer',  action='store_true',  help="Transfer management")
    parser.add_argument('--cpu',  action='store_true',  help="Cpu management")
    parser.add_argument('--memory',  action='store_true',  help="Memory management")
    parser.add_argument('--remove',  action='store_true',  help="Removes snapshot/s")
    parser.add_argument('--create',  action='store_true',  help="Creates a snapshot")
    parser.add_argument('--overwrite',  default=0,  help="Should destination file be overriden")
    args = parser.parse_args(sys.argv[3:])
    resp = None
    if args.moref is not None:
      if args.delete == True:
        url = self.vmware_url + "/vm/" + args.moref + "/-/" + self.sessionid
        resp = requests.delete(url, data=self.http_payload(self.payload)).json()
      elif args.clone == True:
        url = self.vmware_url + "/vm/" + args.moref + "/-/" + self.sessionid
        self.payload['ticket'] = args.ticket
        if args.parent_folder is not None:
          self.payload['parent_folder'] = args.parent_folder
        if args.altername is not None:
          self.payload['altername'] = args.altername
        if args.numcpus is not None:
          self.payload['numcpus'] = args.numcpus
        if args.memorymb is not None:
          self.payload['memorymb'] = args.memorymb
        resp = requests.post(url, data=self.http_payload(self.payload)).json()
      elif args.cdrom == True:
        if args.id is not None:
          url = self.vmware_url + "/vm/" + args.moref + "/cdrom/" + args.id + "/-/" + self.sessionid
          if args.remove == True:
            resp = requests.delete(url, data=self.http_payload(self.payload)).json()
          elif args.change_cdrom == True:
            if args.iso is not None:
              self.payload['iso'] = args.iso
            resp = requests.put(url, data=self.http_payload(self.payload)).json()
          else:
            resp = requests.get(url, data=self.http_payload(self.payload)).json()
        else:
          url = self.vmware_url + "/vm/" + args.moref + "/cdrom/-/" + self.sessionid
          if args.create ==True:
            resp = requests.post(url, data=self.http_payload(self.payload)).json()
          else:
            resp = requests.get(url, data=self.http_payload(self.payload)).json()
      elif args.disk == True:
        if args.id is not None:
          url = self.vmware_url + "/vm/" + args.moref + "/disk/" + args.id + "/-/" + self.sessionid
          if args.remove == True:
            resp = requests.delete(url, data=self.http_payload(self.payload)).json()
          else:
            resp = requests.get(url, data=self.http_payload(self.payload)).json()
        else:
          url = self.vmware_url + "/vm/" + args.moref + "/disk/-/" + self.sessionid
          if args.create ==True:
            self.payload['size'] = args.size
            resp = requests.post(url, data=self.http_payload(self.payload)).json()
          else:
            resp = requests.get(url, data=self.http_payload(self.payload)).json()
      elif args.interface == True:
        if args.id is not None:
          url = self.vmware_url + "/vm/" + args.moref + "/interface/" + args.id + "/-/" + self.sessionid
          if args.remove == True:
            resp = requests.delete(url, data=self.http_payload(self.payload)).json()
          else:
            resp = requests.get(url, data=self.http_payload(self.payload)).json()
        else:
          url = self.vmware_url + "/vm/" + args.moref + "/interface/-/" + self.sessionid
          if args.create ==True:
            resp = requests.post(url, data=self.http_payload(self.payload)).json()
          else:
            resp = requests.get(url, data=self.http_payload(self.payload)).json()
      elif args.powerstatus == True:
        if args.type is not None:
          url = self.vmware_url + "/vm/" + args.moref + "/powerstatus/" + args.type + "/-/" + self.sessionid
          resp = requests.put(url, data=self.http_payload(self.payload)).json()
        else:
          url = self.vmware_url + "/vm/" + args.moref + "/powerstatus/-/" + self.sessionid
          resp = requests.get(url, data=self.http_payload(self.payload)).json()
      elif args.snapshot == True:
        if args.id is not None:
          url = self.vmware_url + "/vm/" + args.moref + "/snapshot/" + args.id + "/-/" + self.sessionid
          if args.remove == True:
            resp = requests.delete(url, data=self.http_payload(self.payload)).json()
          elif args.active == True:
            resp = requests.put(url, data=self.http_payload(self.payload)).json()
          else:
            resp = requests.get(url, data=self.http_payload(self.payload)).json()
        else:
          url = self.vmware_url + "/vm/" + args.moref + "/snapshot/-/" + self.sessionid
          if args.create == True:
            self.payload['name'] = args.name
            if args.desc is not None:
              self.payload['desc'] = args.desc
            resp = requests.post(url, data=self.http_payload(self.payload)).json()
          elif args.remove == True:
            resp = requests.delete(url, data=self.http_payload(self.payload)).json()
          else:
            resp = requests.get(url, data=self.http_payload(self.payload)).json()
      elif args.event == True:
        if args.filter is not None:
          url = self.vmware_url + "/vm/" + args.moref + "/event/" + args.filter + "/-/" + self.sessionid
          resp = requests.get(url, data=self.http_payload(self.payload)).json()
        else:
          url = self.vmware_url + "/vm/" + args.moref + "/event/-/" + self.sessionid
          resp = requests.get(url, data=self.http_payload(self.payload)).json()
      elif args.process == True:
        url = self.vmware_url + "/vm/" + args.moref + "/process/-/" + self.sessionid
        if args.username is not None:
          self.payload['username'] = args.username
        if args.password is not None:
          self.payload['password'] = args.password
        if args.prog is not None:
          self.payload['prog'] = args.prog
          self.payload['workdir'] = args.workdir
          if args.prog_arg is not None:
            self.payload['prog_arg'] = args.prog_arg
          if args.env is not None:
            self.payload['env'] = args.env
          resp = requests.post(url, data=self.http_payload(self.payload)).json()
        else:
          resp = requests.get(url, data=self.http_payload(self.payload)).json()
      elif args.annotation == True:
        if args.delete_annotation == True:
          url = self.vmware_url + "/vm/" + args.moref + "/annotation/" + args.name + "/-/" + self.sessionid
          resp = requests.delete(url, data=self.http_payload(self.payload)).json()
        elif args.change is not None:
          url = self.vmware_url + "/vm/" + args.moref + "/annotation/" + args.name + "/-/" + self.sessionid
          self.payload['value'] = args.change
          resp = requests.put(url, data=self.http_payload(self.payload)).json()
        elif args.name is not None:
          url = self.vmware_url + "/vm/" + args.moref + "/annotation/" + args.name + "/-/" + self.sessionid
          resp = requests.get(url, data=self.http_payload(self.payload)).json()
        else:
          url = self.vmware_url + "/vm/" + args.moref + "/annotation/-/" + self.sessionid
          resp = requests.get(url, data=self.http_payload(self.payload)).json()
      elif args.transfer == True:
        if args.source is not None:
          self.payload['source'] = args.source
          self.payload['username'] = args.username
          self.payload['password'] = args.password
        elif args.dest is not None:
          self.payload['dest'] = args.dest
          self.payload['overwrite'] = args.overwrite
          self.payload['username'] = args.username
          self.payload['password'] = args.password
          self.payload['size'] = args.size
        url = self.vmware_url + "/vm/" + args.moref + "/transfer/-/" + self.sessionid
        resp = requests.post(url, data=self.http_payload(self.payload)).json()
      elif args.cpu == True:
        url = self.vmware_url + "/vm/" + args.moref + "/cpu/-/" + self.sessionid
        if args.numcpus is not None:
          self.payload['numcpus'] = args.numcpus
          resp = requests.put(url, data=self.http_payload(self.payload)).json()
        else:
          resp = requests.get(url, data=self.http_payload(self.payload)).json()
      elif args.memory == True:
        url = self.vmware_url + "/vm/" + args.moref + "/memory/-/" + self.sessionid
        if args.memorymb is not None:
          self.payload['memorymb'] = args.memorymb
          resp = requests.put(url, data=self.http_payload(self.payload)).json()
        else:
          resp = requests.get(url, data=self.http_payload(self.payload)).json()
      else:
        url = self.vmware_url + "/vm/" + args.moref + "/-/" + self.sessionid
        resp = requests.get(url, data=self.http_payload(self.payload)).json()
    else:
      parser.print_help()
      exit(1)
    self.check_status(resp)
    self.output(resp['result'])

  def networks(self):
    self.check_session_exists()
    parser = argparse.ArgumentParser( description='Samu tool for Support',  usage= '''samu.py vmware networks

Example:
  samu.py vmware networks
    ''' + self.global_options)
    resp = None
    url = self.vmware_url + "/network/-/" + self.sessionid
    resp = requests.get(url, data=self.http_payload(self.payload)).json()
    self.check_status(resp)
    for item in resp['result']:
      self.output(item)

  def dvp(self):
    self.check_session_exists()
    parser = argparse.ArgumentParser( description='Samu tool for Support',  usage= '''samu.py vmware dvp [<args>]

Dvp endpoint
  --moref <moref>
  --create
  --ticket <ticket id>
  --switch <switch moref>
  --func <name>
  --delete

Example:
  samu.py vmware dvp
  samu.py vmware dvp --moref dvportgroup-111
  samu.py vmware dvp --create --ticket 1234 --switch dvs-111 --func ha
  samu.py vmware dvp --moref dvportgroup-111 --delete
    ''' + self.global_options)
    parser.add_argument('--moref',  default=None,  help="Moref to a dvp object")
    parser.add_argument('--ticket',  default=None,  help="Ticket id to use")
    parser.add_argument('--switch',  default=None,  help="Parent switch to use")
    parser.add_argument('--func',  default=None,  help="Function for the DVP")
    parser.add_argument('--create',  action='store_true',  help="A DVP should be created in DVS")
    parser.add_argument('--delete',  action='store_true',  help="A DVP should be deleted")
    args = parser.parse_args(sys.argv[3:])
    resp = None
    if args.moref is not None:
      url = self.vmware_url + "/network/dvp/" + args.moref + "/-/" + self.sessionid
      if args.delete == True:
        resp = requests.delete(url, data=self.http_payload(self.payload)).json()
      else:
        resp = requests.get(url, data=self.http_payload(self.payload)).json()
        connected = resp['result'][0]['connected_vms']
        del resp['result'][0]['connected_vms']
        self.output(connected)
    else:
      url = self.vmware_url + "/network/dvp/-/" + self.sessionid
      if args.create == True:
        self.payload['ticket'] = args.ticket
        self.payload['switch'] = args.switch
        self.payload['func'] = args.func
        resp = requests.post(url, data=self.http_payload(self.payload)).json()
      else:
        resp = requests.get(url, data=self.http_payload(self.payload)).json()
    self.check_status(resp)
    self.output(resp['result'])

  def switch(self):
    self.check_session_exists()
    parser = argparse.ArgumentParser( description='Samu tool for Support',  usage= '''samu.py vmware switch [<args>]

Switch endpoint
  --moref <moref>
  --create
  --ticket <ticket id>
  --host <host moref>
  --delete

Example:
  samu.py vmware switch
  samu.py vmware switch --moref dvs-111
  samu.py vmware switch --create --ticket 1234 --host host-111
  samu.py vmware switch --moref dvs-111 --delete
    ''' + self.global_options)
    parser.add_argument('--moref',  default=None,  help="Moref to a switch object")
    parser.add_argument('--ticket',  default=None,  help="Ticket id to use")
    parser.add_argument('--host',  default=None,  help="Parent switch to use")
    parser.add_argument('--create',  action='store_true',  help="A DVP should be created in DVS")
    parser.add_argument('--delete',  action='store_true',  help="A DVP should be deleted")
    args = parser.parse_args(sys.argv[3:])
    resp = None
    if args.moref is not None:
      url = self.vmware_url + "/network/switch/" + args.moref + "/-/" + self.sessionid
      if args.delete == True:
        resp = requests.delete(url, data=self.http_payload(self.payload)).json()
      else:
        resp = requests.get(url, data=self.http_payload(self.payload)).json()
        connected = resp['result'][0]['connected_vms']
        del resp['result'][0]['connected_vms']
        self.output(connected)
    else:
      url = self.vmware_url + "/network/switch/-/" + self.sessionid
      if args.create == True:
        self.payload['ticket'] = args.ticket
        self.payload['host'] = args.host
        resp = requests.post(url, data=self.http_payload(self.payload)).json()
      else:
        resp = requests.get(url, data=self.http_payload(self.payload)).json()
    self.check_status(resp)
    self.output(resp['result'])

  def hostnetwork(self):
    self.check_session_exists()
    parser = argparse.ArgumentParser( description='Samu tool for Support',  usage= '''samu.py vmware hostnetwork [<args>]

Hostnetwork endpoint
  --moref <moref>

Example:
  samu.py vmware hostnetwork 
  samu.py vmware hostnetwork --moref dvs-111
    ''' + self.global_options)
    parser.add_argument('--moref',  default=None,  help="Moref to a hostnetwork object")
    args = parser.parse_args(sys.argv[3:])
    resp = None
    if args.moref is not None:
      url = self.vmware_url + "/network/hostnetwork/" + args.moref + "/-/" + self.sessionid
      resp = requests.get(url, data=self.http_payload(self.payload)).json()
      connected = resp['result'][0]['connected_vms']
      del resp['result'][0]['connected_vms']
      self.output(connected)
    else:
      url = self.vmware_url + "/network/hostnetwork/-/" + self.sessionid
      resp = requests.get(url, data=self.http_payload(self.payload)).json()
    self.check_status(resp)
    self.output(resp['result'])

  def resourcepool(self):
    self.check_session_exists()
    parser = argparse.ArgumentParser( description='Samu tool for Support',  usage= '''samu.py vmware resourcepool [<args>]]

Resourcepool endpoint profile
  --moref <moref>
  --move_child_moref <moref>
  --move_child_type <VMware object type>
  --move_parent <moref>
  --create_name <resourcepool_name>
  --delete

Example:
  samu.py vmware resourcepool 
  samu.py vmware resourcepool --moref resgroup-111

  samu.py vmware resourcepool --create_name herring
  samu.py vmware resourcepool --moref resgroup-111 --create_name herring

  samu.py vmware resourcepool --moref resgroup-111 --delete

  samu.py vmware resourcepool --move_child_moref resgroup-112 --move_child_type Folder 
  samu.py vmware resourcepool --move_child_moref resgroup-112 --move_child_type Folder --move_parent resgroup-111
  samu.py vmware resourcepool --move_child_moref resgroup-112 --move_child_type Folder --moref resgroup-111
    ''' + self.global_options)
    parser.add_argument('--moref',  default=None,  help="Moref of resourcepool")
    parser.add_argument('--delete',  action='store_true',  help="Delete the resourcepool")
    parser.add_argument('--create_name',  default=None,  help="Name of resourcepool to create")
    parser.add_argument('--move_child_moref',  default=None,  help="Child moref to move")
    parser.add_argument('--move_child_type',  default=None,  help="Type of child moref to move")
    parser.add_argument('--move_parent',  default=None,  help="Parent moref to move to")
    args = parser.parse_args(sys.argv[3:])
    resp = None
    if args.moref is not None:
      url = self.vmware_url + "/resourcepool/" + args.moref + "/-/" + self.sessionid
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
        runtime = resp['result'][0]['runtime']
        del resp['result'][0]['runtime']
        self.output([runtime])
    else:
      url = self.vmware_url + "/resourcepool/-/" + self.sessionid
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
    self.check_status(resp)
    self.output(resp['result'])

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
    ''' + self.global_options)
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
    ''' + self.global_options)
    parser.add_argument('--username',  default=None,  help="Username to query")
    args = parser.parse_args(sys.argv[3:])
    resp = None
    if args.username is not None:
      url = self.vmware_url + "/user/" + args.username + "/-/" + self.sessionid
      resp = requests.get(url, data=self.http_payload(self.payload)).json()
    else:
      url = self.vmware_url + "/user/-/" + self.sessionid
      resp = requests.get(url, data=self.http_payload(self.payload)).json()
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
    ''' + self.global_options)
    parser.add_argument('--ticket',  default=None,  help="Moref to Hostsystem object")
    args = parser.parse_args(sys.argv[3:])
    resp = None
    if args.ticket is not None:
      url = self.vmware_url + "/ticket/" + args.ticket + "/-/" + self.sessionid
      resp = requests.get(url, data=self.http_payload(self.payload)).json()
    else:
      url = self.vmware_url + "/ticket/-/" + self.sessionid
      resp = requests.get(url, data=self.http_payload(self.payload)).json()
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
    ''' + self.global_options)
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
    ''' + self.global_options)
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
    ''' + self.global_options)
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
    ''' + self.global_options)
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
    self.check_status(resp)
    self.output(resp['result'])
