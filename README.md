zabbix-apache-stats
===================

Overview
--------
This program gathers data from Apache's built-in status page and 
sends it to Zabbix. The data is sent via the CLI tool zabbix_sender.

*** See http://www.zabbix.com/wiki/templates/apache for a detailed install guide *** 

Author(s)
--------
* Paulson McIntyre (GpMidi) <paul@gpmidi.net>
* Zach Bailey <znbailey@gmail.com>

Install
--------
 1. Run chmod +x on the file
 1. Copy to <some location>, such as /usr/bin/
 1. Add this to crontab: 
        * * * * * /usr/bin/python <some location>/ZabbixApacheUpdater.py --zabbixsource myzabbix -z myzabbixserver &> /dev/null
 1. Replace "myzabbix" with the hostname (or name in the Zabbix GUI) 
of the host that the values should be stored with. Replace "myzqbbixserver" 
with the hostname/IP of your Zabbix server. 
 1. Add this to your Apache config file: 

    ```ApacheConf
    <Location /server-status>
        SetHandler server-status
        Allow from 127.0.0.1
        Order deny,allow
        Deny from all
    </Location>
    ExtendedStatus On # Optional. Must be in global scope and not in a virtual host
    ```
 1. Restart/reload Apache or use ```kill -USR1 `cat /var/run/httpd.pid ```` for zero downtime
 1. Load zabbix_export.xml into Zabbix
 1. Link the Template_App_HTTPd into the hosts in question

License
--------
GPLv2 - See LICENSE file
