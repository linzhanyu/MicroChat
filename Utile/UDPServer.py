#!/usr/bin/env python
# this is the udp broadcast server
import socket, traceback
host = ''                               # Bind to all interfaces
port = 1234
print("python UDP multi case server test")
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s.bind((host, port))
for i  in  range(1,100):
    try:
        s.sendto(b"server here",('192.168.10.255', 2345))
        message, address = s.recvfrom(1234)
        print("Got data from", address,":",message)
        # Acknowledge it.
        s.sendto(b"I am here", address)
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        traceback.print_exc()
