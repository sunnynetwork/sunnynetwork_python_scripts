#!/usr/bin/python
from xml.dom import minidom
from xml.dom.minidom import parse,parseString
from lxml import etree as etree
from ncclient import manager
from ncclient.xml_ import *

conn = 0
vsrx_dictionary = {}
def create_netconf_connection(host, port, user, password):
        global conn
        #connect to router using Netconf
        conn = manager.connect(host=host,username=user,password=password,timeout=10,device_params = {'name':'junos'},hostkey_verify=False)


def parse_route_table(cmd):
    global conn
    global vsrx_dictionary

    #execute command and set return format as xml
    try:
        xml_res = conn.command(command=cmd, format='xml')
    except Exception, e:
        print "get_junos_stats.py encountered critical error"
        print e
        sys.exit(1)

    xml_doc = parseString(xml_res.tostring)
    route_table = xml_doc.getElementsByTagName("route-table")[0]
    table_name = route_table.getElementsByTagName("table-name")[0].firstChild.data
    number_of_active_routes = xml_doc.getElementsByTagName("active-route-count")[0].firstChild.data
    routes = xml_doc.getElementsByTagName("rt")
    vsrx_dictionary["route-table-name"] = table_name
    vsrx_dictionary["active-routes"] = number_of_active_routes
    i = 1

    for route in routes:
        rt_destination = route.getElementsByTagName("rt-destination")[0].firstChild.data
        key = "route-%i-%s"% (i,"destination")
        vsrx_dictionary[key] = rt_destination
        protocol_name = route.getElementsByTagName("protocol-name")[0].firstChild.data
        if (protocol_name == "Access-internal") or (protocol_name == "Static") or (protocol_name == "Direct"):
            via_route = route.getElementsByTagName("via")[0].firstChild.data
            key = "route-%i-%s"% (i,"via")
            vsrx_dictionary[key] = via_route
        elif (protocol_name == "Local"):
            via_route = route.getElementsByTagName("nh-local-interface")[0].firstChild.data
            key = "route-%i-%s"% (i,"via")
            vsrx_dictionary[key] = via_route
        key = "route-%i-%s"% (i,"via")
        vsrx_dictionary[key] = via_route
        i+= 1

create_netconf_connection('192.168.122.35', 830, 'root', 'juniper1')
parse_route_table("show route")
number_of_routes = int(vsrx_dictionary["active-routes"])
print ("=== Route table name =%s, Number of active routes =%i ====" % (vsrx_dictionary["route-table-name"],number_of_routes))
for i in range(1,number_of_routes+1):
        key1 = "route-%i-%s"% (i,"destination")
        key2 = "route-%i-%s"% (i,"via")
        print ("destination-ip=%s,via=%s" % (vsrx_dictionary[key1],vsrx_dictionary[key2]))
