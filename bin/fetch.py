#!/usr/bin/python

""" Fetch Apache stats via mod_status and send to Zabbix 
By Paulson McIntyre
Patches by: 
Zach Bailey <znbailey@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import urllib
from optparse import OptionParser
import os
from tempfile import mkstemp
import StringIO
import csv

class ErrorSendingValues(RuntimeError):
    """ An error occured while sending the values to the Zabbix 
    server using zabbix_sender. 
    """

def fetchURL(url, user = None, passwd = None):
    """ Return the data from a URL """
    if user and passwd:
        parts = url.split('://')
        url = parts[0] + "://" + user + ":" + passwd + "@" + parts[1]
    
    conn = urllib.urlopen(url)
    try:
        data = conn.read()
    finally:
        conn.close()
    return data

def sendValues(filepath, zabbixserver = "localhost", zabbixport = 10051, senderloc = "zabbix_sender"):
    r = os.system("%s --zabbix-server '%s' --port '%s' -i '%s' -vv" % (senderloc, zabbixserver, zabbixport, filepath))
    if r != 0:
        raise ErrorSendingValues, "An error occured sending the values to the server"

def clean(string, chars):
    for i in chars:
        string = string.replace(i, '')
    return string

def parse(data):
    """ Parse the CSV file into a dict of data
    """
    mapping = {
        "_":"Waiting for Connection",
        "S":"Starting up",
        "R":"Reading Request",
        "W":"Sending Reply",
        "K":"Keepalive (read)",
        "D":"DNS Lookup",
        "C":"Closing connection",
        "L":"Logging",
        "G":"Gracefully finishing",
        "I":"Idle cleanup of worker",
        ".":"Open slot with no current process",
        }
    # Clean out certian chars
    replace = '() '
    csvobj = csv.reader(StringIO.StringIO(data), delimiter = ":", skipinitialspace = True)
    ret = {}
    for (key, val) in csvobj:
        if key == 'Scoreboard':
            sb = {
                "Waiting for Connection":0,
                "Starting up":0,
                "Reading Request":0,
                "Sending Reply":0,
                "Keepalive (read)":0,
                "DNS Lookup":0,
                "Closing connection":0,
                "Logging":0,
                "Gracefully finishing":0,
                "Idle cleanup of worker":0,
                "Open slot with no current process":0,
                }
            for i in val:
                sb[mapping[i]] += 1
            ret[key] = sb
        else:
            ret[key] = val
    ret2 = {}
    for (key, val) in ret.items():
        if key == "Scoreboard":
            for (key, val) in val.items():
                ret2[clean(key, replace)] = val
        else:
            ret2[clean(key, replace)] = val
            
    return ret2

if __name__ == "__main__":
    parser = OptionParser(
                        usage = "%prog [-z <Zabbix hostname or IP>] [-o <Apache hostname or IP>]",
                        version = "%prog $Revision: 173 $",
                        prog = "ApacheStatsForZabbix",
                        description = """This program gathers data from Apache's 
built-in status page and sends it to 
Zabbix. The data is sent via zabbix_sender. 
Author: Paulson McIntyre (GpMidi)
License: GPLv2
                        """,
                        )
    parser.add_option(
                      "-l",
                      "--url",
                      action = "store",
                      type = "string",
                      dest = "url",
                      default = None,
                      help = "Override the automatically generated URL with one of your own",
                      )
    parser.add_option(
                      "-o",
                      "--host",
                      action = "store",
                      type = "string",
                      dest = "host",
                      default = "localhost",
                      help = "Host to connect to. [default: %default]",
                      )
    parser.add_option(
                      "-p",
                      "--port",
                      action = "store",
                      type = "int",
                      dest = "port",
                      default = 80,
                      help = "Port to connect on. [default: %default]",
                      )
    parser.add_option(
                      "-r",
                      "--proto",
                      action = "store",
                      type = "string",
                      dest = "proto",
                      default = "http",
                      help = "Protocol to connect on. Can be http or https. [default: %default]",
                      )
    parser.add_option(
                      "-z",
                      "--zabbixserver",
                      action = "store",
                      type = "string",
                      dest = "zabbixserver",
                      default = "localhost",
                      )
    parser.add_option(
                      "-u",
                      "--user",
                      action = "store",
                      type = "string",
                      dest = "user",
                      default = None,
                      help = "HTTP authentication user to use when connection. [default: None]",
                      )
    parser.add_option(
                      "-a",
                      "--passwd",
                      action = "store",
                      type = "string",
                      dest = "passwd",
                      default = None,
                      help = "HTTP authentication password to use when connecting. [default: None]",
                      )
    parser.add_option(
                      "-s",
                      "--sender",
                      action = "store",
                      type = "string",
                      dest = "senderloc",
                      default = "/usr/bin/zabbix_sender",
                      help = "Location to the zabbix_sender executable. [default: %default]",
                      )
    parser.add_option(
                      "-q",
                      "--zabbixport",
                      action = "store",
                      type = "int",
                      dest = "zabbixport",
                      default = 10051,
                      help = "Zabbix port to connect to. [default: %default]",
                      )
    parser.add_option(
                      "-c",
                      "--zabbixsource",
                      action = "store",
                      type = "string",
                      dest = "zabbixsource",
                      default = "localhost",
                      help = "Zabbix host to use when sending values. [default: %default]",
                      )
    (opts, args) = parser.parse_args()
    if opts.url and (opts.port != 80 or opts.proto != "http"):
        parser.error("Can't specify -u with  -p or -r")
    if not opts.url:
        opts.url = "%s://%s:%s/server-status?auto" % (opts.proto, opts.host, opts.port)
    
    data = fetchURL(opts.url, user = opts.user, passwd = opts.passwd)
    
    try:
        (tempfiled, tempfilepath) = mkstemp()
        tempfile = open(tempfilepath, 'wb')
    except:
        parser.error("Error creating temporary file")
        
    try:
        try:
            data = parse(data = data)
        except csv.Error:
            parser.error("Error parsing returned data")
            
        try:
            for key, val in data.items():
                tempfile.write("%s apache[%s,%s] %s\n" % (opts.zabbixsource, opts.host, key, val))
            tempfile.close()
        except "bogus":
            parser.error("Error creating the file to send")
        
        try:
            sendValues(filepath = tempfilepath, zabbixserver = opts.zabbixserver, zabbixport = opts.zabbixport, senderloc = opts.senderloc)
        except ErrorSendingValues:
            parser.error("An error occurred while sending values to the Zabbix server")
            
    finally:
        try:
            tempfile.close()
        except:
            pass
        os.remove(tempfilepath)
    
    
    
        
    
