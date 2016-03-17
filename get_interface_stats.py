#!/usr/bin/python
import sys

from lxml import etree as etree
from ncclient import manager
from ncclient.xml_ import *

conn = 0

def create_netconf_connection(host, port, user, password):
        global conn
        #connect to router using Netconf
        conn = manager.connect(host=host,username=user,password=password,timeout=10,device_params = {'name':'junos'},hostkey_verify=False)

def get_interface_stats(cmd,stat_type):
        global conn

        #execute command and set return format as xml
        try:
          result = conn.command(command=cmd, format='xml')
        except Exception, e:
                print "get_junos_stats.py encountered critical error"
                print e
                sys.exit(1)

        #process xml
        tree = etree.XML(result.tostring)
        traffic_stat = tree.xpath(stat_type)
        return traffic_stat

create_netconf_connection('192.168.122.35', 830, 'root', 'juniper1')
##process traffic statistics
vsrx_stat_dictionary = {}
traffic_statistics_list_t = get_interface_stats('show interface ge-0/0/0 detail statistics','//traffic-statistics')
print "================= Traffic Statistics ================"
total_i_errors = 0
for t_stats in traffic_statistics_list_t[0]:
                vsrx_stat_dictionary[t_stats.tag] = t_stats.text.rstrip()
                print t_stats.tag,'=',t_stats.text.rstrip()

##process traffic input error statistics
input_error_statistics_list = get_interface_stats('show interface ge-0/0/0 detail statistics','//input-error-list')
print "================ Input Error Statistics ============="
for i_error_list in input_error_statistics_list:
        for i_error in i_error_list:
                vsrx_stat_dictionary[i_error.tag] = i_error.text.rstrip()
                print i_error.tag,"=",i_error.text.rstrip()

##process traffic output error statistics
output_error_statistics_list = get_interface_stats('show interface ge-0/0/0 detail statistics','//output-error-list')
print "================ Output Error Statistics ==========="
for o_error_list in output_error_statistics_list:
        for o_error in o_error_list:
                vsrx_stat_dictionary[o_error.tag] = o_error.text.rstrip()
                print o_error.tag,"=",o_error.text.rstrip()
