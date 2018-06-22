'''To query the mavsim map'''


import sys
import socket
import struct

#import actr
import threading
import yaml

import uuid
import itertools

#use a tcp server


mavsim_server = ('127.0.0.1', 32786)
send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#sent = sock.sendto(b'(\'TELEMETRY\', \'SET_MULTICAST\', \'ON\')', server_address)
#sent = send_sock.sendto(b'(\'TELEMETRY\', \'ADD_LISTENER\', \'127.0.0.1\', 9027, 0)', mavsim_server)

def terrain_request(lat=0,lon=0,width=5,height=5):
    startlat = lat - 2
    startlon = lon - 2
    list2 = list(range(startlon,startlon+5))
    list1 = list(range(startlat,startlat+5))

    #print(list1,list2)
    combinations = list(itertools.product(list1,list2))

    terrain_by_pair = []
    #get the terrain at each coordinate from mavsim
    for pair in combinations:
        msg = "('{}', '{}', {}, {})".format('FLIGHT','MS_QUERY_TERRAIN',pair[0],pair[1])
        sent = send_sock.sendto(msg.encode('utf-8'),mavsim_server)
        data,address = send_sock.recvfrom(1024)
        terrain_by_pair.append(data.decode('utf-8'))

    return terrain_by_pair