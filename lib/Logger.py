import logging
import sys

class Logger(object):

  def __init__(self):
    self.ilog = logging.getLogger('samu')
    self.ilog.setLevel(logging.DEBUG)
    # Console printing
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    self.ilog.addHandler(ch)
    #
    self.verbosity = 3
    self.verbosity = self.verbosity_parser()
    #ilog.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  datefmt='%m/%d/%Y %I:%M:%S %p')
  
  def verbosity_parser(self):
    for arg in sys.argv[1:]:
      if arg == '-v':
        self.verbosity += 1
        sys.argv.remove('-v')
      elif arg == '--verbose':
        self.verbosity += 1
        sys.argv.remove('--verbose')
      elif arg == '--quiet':
        self.verbosity -= 1
        sys.argv.remove('--quiet')
      elif arg == '-q':
        self.verbosity -= 1
        sys.argv.remove('-q')
    if self.verbosity > 5:
      self.verbosity = 5
    elif self.verbosity < 0:
      self.verbosity = 0
    print "verbosity is %s " % self.verbosity

  def critical(self, msg):
    # verbosity = 1
    self.ilog.critical(msg)

  def error(self, msg):
    # verbosity = 2
    self.ilog.error(msg)

  def warning(self, msg):
    # verbosity = 3
    self.ilog.warning(msg)

  def info(self, msg):
    # verbosity = 4
    self.ilog.info(msg)

  def debug(self, msg):
    # verbosity = 5
    self.ilog.debug(msg)
