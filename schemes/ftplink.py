# Copyright (C) 1998,1999  marduk <marduk@python.net>
# Copyright (C) 1998,1999 Mike Meyer <mwm@mired.org>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

"""This module defines the functions needed for creating Link objects for urls
using the ftp scheme"""

import urllib
import mimetypes
import ftplib
import urlparse
import myUrlLib
import string
import posixpath
import debugio

Link = myUrlLib.Link

def init(self, url, parent):
    
    self.URL = myUrlLib.basejoin(parent,url)
    self.type = mimetypes.guess_type(url)[0]

    host, port, user, passwd, pathname = parseurl(url)
    try:
	ftp = ftplib.FTP(host,user,passwd)
    	stat(pathname, ftp)
    except ftplib.all_errors, errtext:
	self.set_bad_link(self.URL, str(errtext))
	return

    self.size = size(pathname,ftp)
    if self.size is None: self.size = 0 

def callback(line):
    """Read a line of text and do nothing with it"""
    return

def stat(pathname, ftpobject):
    # This is not completely implemented
    # Note: ftp servers do not respond with a 5xx error when a file does not
    # exist except for GET, which I'm trying to GET around ;-)  Anyway, an
    # error code will be reported if you try to change to a directory that
    # does not exist, so this is not totally useless
    # In addition to the above, all of the ftp servers i tested this on
    # did not report the correct code (211,212,213) when responding to STAT
    # per RFC959.  What the hell is up with that?  Can checking ftp links be
    # done reliably?
    # FTP should be replaced by a new protocol that produces machine-readable
    # responses and actually lets you get the status of a file without having to
    # download it.  Oh wait, that's what HTTP is.
    dirs, filename = split_dirs(pathname)
    cwd(dirs, ftpobject)
    response = ftpobject.retrlines('NLST %s' % filename,callback)
    debugio.write(response,2)

def get_document(url):
    host, port, user, passwd, pathname = parseurl(url)
    dirs, filename = split_dirs(pathname)
    ftp = ftplib.FTP(host,user,passwd)
    cwd(dirs, ftp)
    return ftp.retrbinary('RETR %s' % filename)

def split_dirs(pathname):
    """Given pathname, split it into a tuple consisting of a list of dirs and
    a filename"""
    
    dirs, filename = posixpath.split(pathname)
    dirs = string.split(dirs,'/')
    if dirs[0] == '': dirs[0] = '/'
    if not filename:
	filename = dirs[-1]
	dirs = dirs[:-1]
    return (dirs, filename)

def size(pathname,ftpobject):
    if pathname == '': pathname = '/'
    dirs, filename = split_dirs(pathname)
    debugio.write('pathname =%s' % pathname,3)
    debugio.write('dirs= %s' % dirs,3)
    debugio.write('filename= %s' % filename,3)
    cwd(dirs, ftpobject)
    return ftpobject.size(filename)

def cwd(dirs, ftpobject):
    for dir in dirs:
	ftpobject.cwd(dir)

def parseurl(url):
    parsed = urlparse.urlparse(url)
    host = parsed[1]
    if '@' in host:
	userpass, host = string.split(host,'@')
	if ':' in userpass:
	    user, passwd = string.split(userpass,':')
	else:
	    user = userpass
	    passwd = None
    else:
	user = 'anonymous'
	# this is bad, i'll change it later
	passwd = 'mwm@mired.org'

    if ':' in host:
	host, port = string.split(host,':')
	port = int(port)
    else:
	port = ftplib.FTP_PORT

    pathname = parsed[2]
    if not port: port = ftplib.FTP_PORT
    return (host, port, user, passwd, pathname)
