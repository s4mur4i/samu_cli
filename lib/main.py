from __future__ import print_function, absolute_import
import os
import sys
import time
import imp
import argparse

def option_parser( root_dir):
    argument = ''
    if len(sys.argv) > 0:
        argument = sys.argv.pop(0)
    print("argument: " , argument)
    try:
        path = root_dir + "/lib/commands"
        print("path: " , path)
        f, path, desc = imp.find_module( argument, [ path] )
    except ImportError:
        print('Bang')
#        parser = argparse.ArgumentParser()
#        parser.print_help()

def app_main(started_at, root_dir):
    self = sys.argv.pop(0)
    option_parser( root_dir );
