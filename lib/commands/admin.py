from base import ObjectS
import sys
import argparse
import requests

class Admin(ObjectS):

  def __init__(self, logger = None):
    self.logger = logger
    super(Admin, self).__init__(logger=self.logger)
    self.logger.info('Admin module entry endpoint')

  def start(self):
    self.logger.info('Invoked starting point for Admin')
    self.admin_url = self.samu_url + '/admin'
    self.parser = argparse.ArgumentParser( description='Samu tool for Support',  usage= ''' samu.py <command> [<args>]]

Second level options are following:
  profile
  logout
  roles
  users
  config
  register

Global Options:
  -v, --verbose       increment verbosity level (max 5)
  -q, --quiet         decrease verbosity level (max 0)
  # Default verbosity level 3
  # Following options defaults to config file but can be overriden
  # with these arguments
  --samu_username     Username to use for samu
  --samu_password     Password to use for samu
  --samu_url          Url for samu Rest API
  --vcenter_username  Username to Vcenter
  --vcenter_password  Password to Vcenter
  --vcenter_url       SDK url for Vcenter
    ''')
    self.parser.add_argument('command',   help='Command to run')
    args = self.parser.parse_args(sys.argv[2:3])
    if not hasattr(self,  args.command):
      self.logger.error('Unrecognized command')
      self.parser.print_help()
      exit(1)
    getattr(self,  args.command)()

  def profile(self):
    print "To be implemented"
    exit(1)

  def logout(self):
    self.get_sessionid()
    resp = requests.get(self.admin_url + '/logoff/-/' + self.sessionid).json()
    self.check_status(resp)
    print "Session id %s logged out" % self.sessionid

  def roles(self):
    print "To be implemented"
    exit(1)

  def users(self):
    print "To be implemented"
    exit(1)

  def config(self):
    print "To be implemented"
    exit(1)
  
  def register(self):
    parser = argparse.ArgumentParser( description='Samu tool for Support',  usage= ''' samu.py <command> [<args>]]

Register endpoint:
  --email
  --username
  --password
    ''')
    parser.add_argument('--email',  default=None,  help="Email address of user")
    parser.add_argument('--username',  default=None,  help='Username of user')
    parser.add_argument('--password',  default=None,  help='Requested password for user')
    args = parser.parse_args(sys.argv[3:])
    payload = {'username': args.username,  'email': args.email, 'password': args.password}
    resp = requests.post(self.admin_url,  data=payload).json()
    self.check_status(resp)
    print "User has been registered with %s username and id of %s " % ( args.username, resp['result'][0]['id'])
    print "Please update samu.config in your home directory"
