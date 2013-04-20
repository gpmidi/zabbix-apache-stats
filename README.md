zabbix-apache-stats
===================

Overview
--------
This program gathers data from Apache's 
built-in status page and sends it to 
Zabbix. The data is sent via zabbix_sender.

*** See http://www.zabbix.com/wiki/templates/apache for a detailed install guide *** 

Author(s)
--------
* Paulson McIntyre (GpMidi)

Install
--------
1) Run chmod +x on the file
2) Copy to <some location>, such as /usr/bin/
3) Add this to crontab: 
* * * * * /usr/bin/python <some location>/ZabbixApacheUpdater.py --zabbixsource myzabbix -z myzabbixserver &> /dev/null
4) Replace "myzabbix" with the hostname (or name in the Zabbix GUI) 
of the host that the values should be stored with. Replace "myzqbbixserver" 
with the hostname/IP of your Zabbix server. 
5) Add this to your Apache config file
<Location /server-status>
        SetHandler server-status
        Allow from 127.0.0.1
        Order deny,allow
        Deny from all
</Location>
ExtendedStatus On # Optional. Must be in global scope and not in a virtual host
6) Restart/reload Apache or use "kill -USR1 `cat /var/run/httpd.pid `" for zero downtime
7) Load zabbix_export.xml into Zabbix
8) Link the Template_App_HTTPd into the hosts in question

License
--------
GPLv2 - See LICENSE file
