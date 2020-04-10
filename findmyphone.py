# preinstall
# https://github.com/karulis/pybluez/tree/master
# https://github.com/BlackLight/PyOBEX
# 

import bluetooth
from PyOBEX.client import Client

def finished() -> None:
    print('finished')

print("performing inquiry...")

nearby_devices = bluetooth.discover_devices(
        duration=8, lookup_names=True, flush_cache=True, lookup_class=False)

print("found %d devices" % len(nearby_devices))

obex_object_push_devices = []
for addr, name in nearby_devices:
    try:
        print("  %s - %s" % (addr, name))
        service_matches = bluetooth.find_service(name=b'OBEX Object Push\x00', address = addr)
        if len(service_matches) > 0:
            print("found OBEX push service in %s" % name)
            obex_object_push_devices.append(addr)

    except UnicodeEncodeError:
        print("  %s - %s" % (addr, name.encode('utf-8', 'replace')))

import sys

# if len(sys.argv) < 2:
#     print("usage: sdp-browse <addr>")
#     print("   addr can be a bluetooth address, \"localhost\", or \"all\"")
#     sys.exit(2)

if len(obex_object_push_devices) == 0:
    sys.exit(2)

target = obex_object_push_devices[0]
services = bluetooth.find_service(address=target)

if len(services) > 0:
    print("found %d services on %s" % (len(services), addr))
    print("")
else:
    print("no services found")
    sys.exit(0)

for svc in services:
    print("Service Name: %s"    % svc["name"])
    print("    Address:  %s" % svc["host"])
    #print("    Description: %s" % svc["description"])
    #print("    Provided By: %s" % svc["provider"])
    #print("    Protocol:    %s" % svc["protocol"])
    print("    channel/PSM: %s" % svc["port"])
    #print("    svc classes: %s "% svc["service-classes"])
    #print("    profiles:    %s "% svc["profiles"])
    #print("    service id:  %s "% svc["service-id"])
    print("")


# find OBEX Object Push service
service_matches = bluetooth.find_service(name=b'OBEX Object Push\x00', address = addr )

if len(service_matches) == 0:
    print("Couldn't find the service.")
    sys.exit(0)

first_match = service_matches[0] # OBEX Object Push
port = first_match["port"]
name = first_match["name"]
host = first_match["host"]

print("connecting to \"%s\" on %s:%s" % (name, host, port))
client = Client(host, port)

client.connect()
print("sending file...")
client.put("test.txt", "Hello world\n")
client.disconnect()


