'''To query the mavsim map'''


import sys
import socket
import struct

#import actr
import threading
import yaml

import uuid

#use a tcp server


mavsim_server = ('127.0.0.1', 32786)
send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#sent = sock.sendto(b'(\'TELEMETRY\', \'SET_MULTICAST\', \'ON\')', server_address)
sent = send_sock.sendto(b'(\'TELEMETRY\', \'ADD_LISTENER\', \'127.0.0.1\', 9027, 0)', mavsim_server)