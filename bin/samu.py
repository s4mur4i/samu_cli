#!/usr/bin/env python
# vim: sts=2 ts=2 et ai

import time
start_time = time.time()

import errno
import os
import sys

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

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(resolve_link_chain(os.path.abspath(sys.argv[0])))))
if os.path.samefile(sys.argv[0], root_dir + '/bin/samu.py'):
    os.environ['SAMU_ROOT'] = root_dir
else:
    print("The script started as a symlink doesn't point to it's own script (to '{0}/bin/samu.py'))".format(root_dir))
    sys.exit(1)

samu_lib_dir = "%s/lib" % (root_dir,)
sys.path.append(samu_lib_dir)

from main import app_main
app_main(start_time, root_dir)
