#!/usr/bin/env python
# -*- coding: latin-1 -*-#
#@+leo-ver=5-thin
#@+node:maphew.20110908163305.1242: * @file register-python.py
#@@first
#@@first
#@+<<docstring>>
#@+node:maphew.20110909213512.1219: ** <<docstring>>
# script to register Python 2.0 or later for use with win32all
# and other extensions that require Python registry settings
#
# written by Joakim Löw for Secret Labs AB / PythonWare
#
# modified by Matt Wilkie for OSGeo4W
#
# Adapted from:
#   http://www.pythonware.com/products/works/articles/regpy20.htm
#   http://effbot.org/zone/python-register.htm
#   http://timgolden.me.uk/python-on-windows/programming-areas/registry.html
#
# Known problems:
#   Doesn't detect existing python registrations on 64bit machines,
#   see http://www.mail-archive.com/python-list@python.org/msg266397.html
#

#@-<<docstring>>
#@@language python
#@@tabwidth -4
#@+<<imports>>
#@+node:maphew.20110908224431.1214: ** <<imports>>
import sys
from _winreg import *

#@-<<imports>>
#@+others
#@+node:maphew.20110914213235.1221: ** parse command line
__version__ = '2011-09-14.20:47'
# print '-={ %s }=-\n'% (str.strip(svn_id, ' $'))    
#@verbatim
#@url http://www.doughellmann.com/PyMOTW/argparse/

import argparse, sys

# url http://stackoverflow.com/questions/4042452/display-help-message-with-python-argparse-when-script-is-called-without-any-argum
# display the usage message when it is called with no arguments
class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

parser=MyParser()
parser.add_argument('action', help='one of "install" or "remove" ')
args = vars(parser.parse_args())

#@+node:maphew.20110909213512.1220: ** environment & variables
# grab some details of python environment running this script
our_version = sys.version[:3]
our_installpath = sys.prefix

# the registry key paths we'll be looking at & using
pycore_regpath = "SOFTWARE\\Python\\Pythoncore\\"
installkey = "InstallPath"
pythonkey = "PythonPath"

pythonpath = "%s;%s\\Lib\\;%s\\DLLs\\" % \
        (our_installpath, our_installpath, our_installpath)
        
#@+node:maphew.20110908224431.1215: ** get_existing
def get_existing(hkey, pycore_regpath):
    ''' retrieve existing python registrations '''

    if hkey == 'Current':
        try:
            key = OpenKey(HKEY_CURRENT_USER, pycore_regpath)
        except WindowsError:
            #print WindowsError()
            return
    elif hkey == 'All':
        try:
            key = OpenKey(HKEY_LOCAL_MACHINE, pycore_regpath)
        except WindowsError:
            #print WindowsError()
            return

    i = 0
    versions = {}
    while True:
        try:
            ver = (EnumKey (key, i))                                      # e.g. '2.7'
            install_path = QueryValue(key, ver + '\\installpath')  # e.g. HKLM\\SOFTWARE\\Python\\PythonCore\\2.7\\InstallPath
            versions[ver] = install_path                                   # e.g. {'2.7' = 'C:\\Python27'}
            i += 1
            # print versions
        except EnvironmentError:
            break
    return versions
#@+node:maphew.20110908224431.1216: ** RegisterPy
def RegisterPy(pycore_regpath, version):
    ''' put this python install into registry '''
    pycore_regpath = pycore_regpath + version
    try:
        reg = OpenKey(HKEY_LOCAL_MACHINE, pycore_regpath)
        regVal = QueryValueEx(reg, installkey)[0]
        print regVal
    except EnvironmentError:
        try:
            reg = CreateKey(HKEY_LOCAL_MACHINE, pycore_regpath)
            SetValue(reg, installkey, REG_SZ, our_installpath)
            SetValue(reg, pythonkey, REG_SZ, pythonpath)
            CloseKey(reg)
        except:
            print "*** Unable to register!"
            return
        print "--- Python %s is now registered to %s!" % (our_version, our_installpath)
        return
    if (QueryValue(reg, installkey) == our_installpath and
        QueryValue(reg, pythonkey) == pythonpath):
        CloseKey(reg)
        print "=== Python %s is already registered!" % (our_version)
        return
    CloseKey(reg)
    print "*** Unable to register!"
    print "*** You probably have another Python installation!"

#@-others

if args['action']=='install':
    print args
    # look for existing python registrations
    CurrentUser = get_existing('Current',pycore_regpath)
    AllUsers = get_existing('All',pycore_regpath)
    
    if CurrentUser:
        print '\nFound in Current User:'
        for key in CurrentUser:
            print "\n\t%s - %s\n" % (key, CurrentUser[key])
    if AllUsers:
        print '\nFound in All Users:'
        for key in AllUsers:
            print "\n\t%s - %s\n" % (key, AllUsers[key])
                    
    
    # see if any existing registrations match our python version
    # and if not, register ours
    if CurrentUser:
        match = True if our_version in CurrentUser else False
        versions = CurrentUser
    elif AllUsers:
        match = True if our_version in AllUsers else False
        versions = AllUsers
    else:
        RegisterPy(pycore_regpath,our_version)
    
    try:
        if match:
            print '\nOur version (%s) already registered to "%s", skipping...' % (our_version, versions[our_version])
    except:
        pass

if args['action']=='remove':
    print args

if not 'install' or 'remove' in args:
    print 'jhlp'
            
#-- the end
#@-leo
