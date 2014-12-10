#!/usr/bin/env python
# vim: sts=2 ts=2 et ai
# https://github.com/kislyuk/argcomplete
# Investigate for later 
import time
start_time = time.time()

import errno
import os
import sys
import argparse

def resolve_link_chain(path):
    try:
        os.stat(path)
    except os.error as err:
        # do not raise exception in case of broken symlink
        # we want to know the final target anyway
        if err.errno == errno.ENOENT:
            pass
        else:
            raise
    if not os.path.isabs(path):
        basedir = os.path.dirname(os.path.abspath(path))
    else:
        basedir = os.path.dirname(path)
    p = path
    while os.path.islink(p):
        p = os.readlink(p)
        if not os.path.isabs(p):
            p = os.path.join(basedir, p)
            basedir = os.path.dirname(p)
    return os.path.join(basedir, p)

class Initiator(object):
  
  def __init__(self, logger = None ):
    self.logger = logger
    parser = argparse.ArgumentParser( description='Samu tool for Support', usage= ''' samu.py <command> [<args>]
    
First level options are following:
  admin               user related interface
  vmware              vmware related interface
  kayako              kayako related interface
  devel               development interface

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
    parser.add_argument('command',  help='Command to run')
    args = parser.parse_args(sys.argv[1:2])
    if not hasattr(self, args.command):
      self.logger.error('Unrecognized command')
      parser.print_help()
      exit(1)
    getattr(self, args.command)()
    
  def admin(self):
    self.logger.info('First endpoint for admin')
    from admin import Admin
    a = Admin( logger = self.logger)
    a.start()

  def vmware(self):
    self.logger.info('First endpoint for vmware')
    from vmware import Vmware
    a = Vmware( logger = self.logger)
    a.start()

  def kayako(self):
    self.logger.debug('Not implemented yet')
    exit(1)

  def devel(self):
    self.logger.debug('Not implemented yet')
    exit(1)

if __name__ == '__main__':
  root_dir = os.path.dirname(os.path.dirname(os.path.abspath(resolve_link_chain(os.path.abspath(sys.argv[0])))))
  if os.path.samefile(sys.argv[0], root_dir + '/bin/samu.py'):
      os.environ['SAMU_ROOT'] = root_dir
  else:
      print("The script started as a symlink doesn't point to it's own script (to '{0}/bin/samu.py'))".format(root_dir))
      sys.exit(1)

  samu_lib_dir = "%s/lib" % (root_dir,)
  sys.path.append(samu_lib_dir)
  samu_commands_dir = "%s/lib/commands/" % (root_dir,)
  sys.path.append(samu_commands_dir)
  # Samu specific logger
  from Logger import Logger
  logger = Logger()
  logger.debug('Starting Initiator')
  Initiator( logger=logger )
