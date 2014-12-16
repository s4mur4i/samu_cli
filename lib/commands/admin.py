from base import ObjectS
import sys
import argparse
import requests

class Admin(ObjectS):

  def __init__(self, logger = None, global_options = None):
    self.logger = logger
    self.global_options = global_options
    super(Admin, self).__init__(logger=self.logger)
    self.logger.info('Admin module entry endpoint')

  def start(self):
    self.logger.info('Invoked starting point for Admin')
    self.admin_url = self.samu_url + '/admin'
    parser = argparse.ArgumentParser( description='Samu tool for Support',  usage= '''samu.py <command> [<args>]]

Second level options are following:
  profile
  logout
  roles
  users
  config
  register
    ''' + self.global_options)
    parser.add_argument('command',   help='Command to run')
    args = parser.parse_args(sys.argv[2:3])
    if not hasattr(self,  args.command):
      self.logger.error('Unrecognized command')
      parser.print_help()
      exit(1)
    getattr(self,  args.command)()

  def profile(self):
    self.get_sessionid()
    parser = argparse.ArgumentParser( description='Samu tool for Support',  usage= '''samu.py admin profile [<args>]]

User endpoint args:
  --id <user_id>
  --delete
  --update
  --username <username>
  --email <email>
  --password <password>

Example:
  samu.py admin profile 
  samu.py admin profile --id 1
  samu.py admin profile --id 1 --delete
  samu.py admin profile --id 1 --update --username herring --email herring@sea.xxx --password tunafish
    ''' + self.global_options)
    parser.add_argument('--id', default=None, help="Get profile of specific id")
    parser.add_argument('--delete', action='store_true', help="Delete a specific user")
    parser.add_argument('--update', action='store_true', help="Update should be done to settings")
    parser.add_argument('--username', default=None, help="Change the username")
    parser.add_argument('--password', default=None, help="Change the password")
    parser.add_argument('--email', default=None, help="Change the email address")
    args = parser.parse_args(sys.argv[3:])
    resp = None
    if args.id is not None:
      url = self.admin_url + '/profile/' + args.id + '/-/' + self.sessionid
      self.logger.debug("URL for download is: %s" % url)
      if args.delete is True:
        resp = requests.delete(url, data=self.http_payload()).json()
      elif args.update is True:
        payload = {}
        if args.username is not None:
          payload['username'] = args.username
        if args.password is not None:
          payload['password'] = args.password
        if args.email is not None:
          payload['email'] = args.email
        resp = requests.post(url, data=self.http_payload(payload)).json()
      else:
        resp = requests.get(url, data=self.http_payload()).json()
    else:
      url = self.admin_url + '/profile/-/' + self.sessionid
      self.logger.debug("URL for download is: %s" % url)
      resp = requests.get(url, data=self.http_payload()).json()
    self.logger.debug("Response is: %s" % resp)
    self.check_status(resp)
    self.output(resp['result'])

  def logout(self):
    self.get_sessionid()
    resp = requests.get(self.admin_url + '/logoff/-/' + self.sessionid, data=self.http_payload()).json()
    self.check_status(resp)
    print "Session id %s logged out" % self.sessionid

  def roles(self):
    self.get_sessionid()
    parser = argparse.ArgumentParser( description='Samu tool for Support',  usage= '''samu.py admin roles [<args>]]

Roles endpoint args:
  --role <role_name>     List, remove, update users in a role
  --remove <user_id>     User to remove from role
  --update <user_id>     User to give specific role

Example:
  samu.py admin roles 
  samu.py admin roles --role admin
  samu.py admin roles --role admin --remove 1
  samu.py admin roles --role admin --update 1
    ''' + self.global_options)
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
    self.get_sessionid()
    parser = argparse.ArgumentParser( description='Samu tool for Support',  usage= '''samu.py admin users [<args>]]

User endpoint args:
  --username <user_id>

Example:
  samu.py admin users
  samu.py admin users --username herring
    ''' + self.global_options)
    parser.add_argument('--username', default=None, help="Get id of specific username")
    args = parser.parse_args(sys.argv[3:])
    resp = None
    if args.username is not None:
      url = self.admin_url + '/list/' + args.username + '/-/' + self.sessionid
      resp = requests.get(url, data=self.http_payload()).json()
    else:
      url = self.admin_url + '/list/-/' + self.sessionid
      resp = requests.get(url, data=self.http_payload()).json()
    self.logger.debug("Response is: %s" % resp)
    self.check_status(resp)
    self.output(resp['result'])

  def config(self):
    self.get_sessionid()
    parser = argparse.ArgumentParser( description='Samu tool for Support',  usage= '''samu.py admin config [<args>]]

Config endpoint args:
  --id <userid>
  --update
  --delete
  --name <configuration option name>
  --value <value of configuration>

Example:
  samu.py admin config --id <userid>
  samu.py admin config --id <userid> --delete --name mac_base
  samu.py admin config --id <userid> --update --name mac_base --value 00:11:22:
    ''' + self.global_options)
    parser.add_argument('--id', default=None, help="Get profile of specific id")
    parser.add_argument('--update', action='store_true', help="The configuration option should be updated")
    parser.add_argument('--delete', action='store_true', help="The configration option should be removed from database")
    parser.add_argument('--name', default=None, help="Name of configuration option")
    parser.add_argument('--value', default=None, help="Value of configration option")
    args = parser.parse_args(sys.argv[3:])
    resp = None
    url = self.admin_url + '/profile/' + args.id + '/configs/-/' + self.sessionid 
    if args.update == True:
      payload = { 'name': args.name, 'value':args.value }
      resp = requests.post(url, data=self.http_payload(payload)).json()
    if args.delete == True:
      payload = { 'name': args.name }
      resp = requests.delete(url, data=self.http_payload(payload)).json()
    else:
      resp = requests.get(url, data=self.http_payload()).json()
    self.logger.debug("Response is: %s" % resp)
    self.check_status(resp)
    self.output(resp['result'])

  def register(self):
    parser = argparse.ArgumentParser( description='Samu tool for Support',  usage= '''samu.py admin register [<args>]]

Register endpoint args:
  --email
  --username
  --password

Example:
  samu.py admin register --email herring@sea.com --username herring --password tunafish
    ''' + self.global_options)
    parser.add_argument('--email',  default=None,  help="Email address of user")
    parser.add_argument('--username',  default=None,  help='Username of user')
    parser.add_argument('--password',  default=None,  help='Requested password for user')
    args = parser.parse_args(sys.argv[3:])
    payload = {'username': args.username,  'email': args.email, 'password': args.password}
    resp = requests.post(self.admin_url,  data=self.http_payload(payload)).json()
    self.check_status(resp)
    print "User has been registered with %s username and id of %s " % ( args.username, resp['result'][0]['id'])
    print "Please update samu.config in your home directory"
    print "Skeleton can be found in $samu_root_dir/etc folder"
