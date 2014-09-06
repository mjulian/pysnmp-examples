#!/usr/bin/env python
from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.smi import builder
import time
import socket
import struct
import pickle

hostname = socket.gethostname().split('.')
colo = hostname[1]

CARBON_SERVER = ""
CARBON_PORT = 2004

COMMUNITY_STRING = ""


cmdGen = cmdgen.CommandGenerator()
mibBuilder = cmdGen.snmpEngine.msgAndPduDsp.mibInstrumController.mibBuilder
mibSources = mibBuilder.getMibSources() + (
    builder.DirMibSource('/opt/pymibs'),
    )
mibBuilder.setMibSources(*mibSources)


def get_slb_list():
    # This function commented out for proprietary reasons
    # You can build this list statically or using some external
    # data source (I prefer to query SQL or an API)
    return


def send_metrics(metric_data):
    package = pickle.dumps(metric_data, 1)
    size = struct.pack('!L', len(package))
    sock = socket.socket()
    sock.connect((CARBON_SERVER, CARBON_PORT))
    sock.sendall(size)
    sock.sendall(package)


def poll_f5_virtual_service(slb):
    """
    This function takes the FQDN of an SLB and polls via SNMP
    for the current connections on a VIP. The results are formatted
    into a Graphite metric, pickled, and sent to Graphite.

    SLB name, as sent to Graphite, is only the short name (the name before
    the first domain suffix, eg, slb1a).
    """
    slb_name, colo, domain = slb.split('.', 2)
    metric_data = ([])
    errorIndication, errorStatus, errorIndex, varBindTable = cmdGen.nextCmd(
        cmdgen.CommunityData(COMMUNITY_STRING),
        cmdgen.UdpTransportTarget((slb, 161)),
        cmdgen.MibVariable('F5-BIGIP-LOCAL-MIB', 'ltmVirtualServStatClientCurConns'),
        lookupValues=True,
        lookupNames=True,
    )

    for varBindTableRow in varBindTable:
        for name, val in varBindTableRow:
            customer, service = name.prettyPrint().lstrip("F5-BIGIP-LOCAL-MIB::ltmVirtualServStatClientCurConns.").strip('\"').lstrip('/').split('/')
            val = int(val.prettyPrint())
            metric_data.append(('slb.%s.%s.%s.%s' % (colo, slb_name, customer, service), (int(time.time()), val)))
    send_metrics(metric_data)


if __name__ == "__main__":
    for device_name, device_colo, device_model in get_slb_list():
        if device_colo == colo:
            poll_f5_virtual_service(device_name)
