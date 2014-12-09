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
    parser = argparse.ArgumentParser( description='Samu tool for Support',  usage= ''' samu.py <command> [<args>]]

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
    getattr(self,  args.command)()

  def profile(self):
    print "To be implemented"
    exit(1)

  def logout(self):
    self.get_sessionid()
    resp = requests.get(self.admin_url + '/logoff/-/' + self.sessionid, data=self.http_payload()).json()
    self.check_status(resp)
    print "Session id %s logged out" % self.sessionid

  def roles(self):
    self.get_sessionid()
    parser = argparse.ArgumentParser( description='Samu tool for Support',  usage= ''' samu.py admin roles [<args>]]

Roles endpoint args:
  --role <role_name>     List, remove, update users in a role
  --remove <user_id>     User to remove from role
  --update <user_id>     User to give specific role

Example:
  samu.py admin roles 
  samu.py admin roles --role admin
  samu.py admin roles --role admin --remove 1
  samu.py admin roles --role admin --update 1
    ''')
    parser.add_argument('--role', default=None, help="Endpoint for specific role")
    parser.add_argument('--remove', default=None, help="Remove specific user id")
    parser.add_argument('--update', default=None, help="Add specific user id")
    args = parser.parse_args(sys.argv[3:])
    resp = None
    if args.role == None:
      url = self.admin_url + '/roles/-/' + self.sessionid
      self.logger.debug("URL for download is: %s" % url)
      resp = requests.get(url, data=self.http_payload()).json()
    else:
      url = self.admin_url + '/roles/' + args.role + '/-/' + self.sessionid
      self.logger.debug("URL for download is: %s" % url)
      if args.remove is not None:
        resp = requests.delete(url, data=self.http_payload({'user_id': args.remove, 'role': args.role})).json()
      if args.update is not None:
        resp = requests.post(url, data=self.http_payload({'user_id': args.update, 'role': args.role})).json()
      else:
        resp = requests.get(url, data=self.http_payload()).json()
    self.logger.debug("Response is: %s" % resp)
    self.check_status(resp)
    self.output(resp['result'])

  def users(self):
    print "To be implemented"
    exit(1)

  def config(self):
    print "To be implemented"
    exit(1)
  
  def register(self):
    parser = argparse.ArgumentParser( description='Samu tool for Support',  usage= ''' samu.py admin register [<args>]]

Register endpoint args:
  --email
  --username
  --password
    ''')
    parser.add_argument('--email',  default=None,  help="Email address of user")
    parser.add_argument('--username',  default=None,  help='Username of user')
    parser.add_argument('--password',  default=None,  help='Requested password for user')
    args = parser.parse_args(sys.argv[3:])
    payload = {'username': args.username,  'email': args.email, 'password': args.password}
    resp = requests.post(self.admin_url,  data=self.http_payload(payload)).json()
    self.check_status(resp)
    print "User has been registered with %s username and id of %s " % ( args.username, resp['result'][0]['id'])
    print "Please update samu.config in your home directory"
