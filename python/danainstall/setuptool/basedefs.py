#-*- coding: utf-8 -*-
#vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

"""
This module provides all the predefined variables.
"""

import datetime
import os
import sys
import tempfile

from utils import get_current_user



DANAINSTALL_VAR_DIR = '/var/tmp/danainstall'
try:
    os.mkdir(DANAINSTALL_VAR_DIR, 0o700)
except OSError:
    # directory is already created, check ownership
    stat = os.stat(DANAINSTALL_VAR_DIR)
    if stat.st_uid == 0 and os.getuid() != stat.st_uid:
        print ('%s is already created and owned by root. Please change '
               'ownership and try again.' % DANAINSTALL_VAR_DIR)
        sys.exit(1)
finally:
    uid, gid = get_current_user()

    if uid != 0 and os.getuid() == 0:
        try:
            os.chown(DANAINSTALL_VAR_DIR, uid, gid)
        except Exception as ex:
            print ('Unable to change owner of %s. Please fix ownership '
                   'manually and try again.' % DANAINSTALL_VAR_DIR)
            sys.exit(1)

_tmpdirprefix = datetime.datetime.now().strftime('%Y%m%d-%H%M%S-')
VAR_DIR = tempfile.mkdtemp(prefix=_tmpdirprefix, dir=DANAINSTALL_VAR_DIR)
DIR_LOG = VAR_DIR
FILE_LOG = 'dana-setup.log'

LATEST_LOG_DIR = '%s/latest' % DANAINSTALL_VAR_DIR
if os.path.exists(LATEST_LOG_DIR):
    try:
        os.unlink(LATEST_LOG_DIR)
    except OSError:
        print ('Unable to delete symbol link for log dir %s.' % LATEST_LOG_DIR)

try:
    # Extract folder name at /var/tmp/danainstall/<VAR_DIR> and do a relative
    # symlink to /var/tmp/danainstall/latest
    os.symlink(os.path.basename(VAR_DIR),
               os.path.join(DANAINSTALL_VAR_DIR, 'latest'))
except OSError:
    print ('Unable to create symbol link for log dir %s.' % LATEST_LOG_DIR)


FILE_INSTALLER_LOG = "setup.log"

DIR_PROJECT_DIR = os.environ.get('INSTALLER_PROJECT_DIR', os.getcwd())
DIR_PLUGINS = os.path.join(DIR_PROJECT_DIR, "plugins")

PACKAGE_DIR = os.path.join(DIR_PROJECT_DIR, "package")

DANA_DIR = "/opt/dana"

INSTALL_CACHE_DIR = "/opt/dana/installtmp"

