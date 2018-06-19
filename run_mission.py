import sys
import socket
import struct

#import actr
import threading
import yaml
import uuid




uuid = uuid.uuid4().hex
print("uuid", uuid)

mavsim_server = ('127.0.0.1', 32786)
send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
msg = '(\'SIM\', \'NEW\', \'godiland-base\', \'{}\')'.format(uuid)
sent = send_sock.sendto(msg.encode('utf-8'), mavsim_server)
msg = '(\'FLIGHT\', \'ARM\')'
sent = send_sock.sendto(msg.encode('utf-8'), mavsim_server)
msg = '(\'FLIGHT\', \'MS_LOAD_PAYLOAD\', 0, \'food\')'
sent = send_sock.sendto(msg.encode('utf-8'), mavsim_server)
msg = '(\'FLIGHT\',\'AUTO_TAKEOFF\')'
sent = send_sock.sendto(msg.encode('utf-8'), mavsim_server)
msg = '(\'FLIGHT\',\'MS_NO_ACTION\')'
sent = send_sock.sendto(msg.encode('utf-8'), mavsim_server)
sent = send_sock.sendto(msg.encode('utf-8'), mavsim_server)
sent = send_sock.sendto(msg.encode('utf-8'), mavsim_server)
sent = send_sock.sendto(msg.encode('utf-8'), mavsim_server)
sent = send_sock.sendto(msg.encode('utf-8'), mavsim_server)
sent = send_sock.sendto(msg.encode('utf-8'), mavsim_server)
sent = send_sock.sendto(msg.encode('utf-8'), mavsim_server)
sent = send_sock.sendto(msg.encode('utf-8'), mavsim_server)
sent = send_sock.sendto(msg.encode('utf-8'), mavsim_server)
sent = send_sock.sendto(msg.encode('utf-8'), mavsim_server)
msg = '(\'FLIGHT\', \'FLY_TO\', 485, 29, 3)'
sent = send_sock.sendto(msg.encode('utf-8'), mavsim_server)
msg = '(\'FLIGHT\',\'MS_NO_ACTION\')'
sent = send_sock.sendto(msg.encode('utf-8'), mavsim_server)
sent = send_sock.sendto(msg.encode('utf-8'), mavsim_server)
sent = send_sock.sendto(msg.encode('utf-8'), mavsim_server)
sent = send_sock.sendto(msg.encode('utf-8'), mavsim_server)
sent = send_sock.sendto(msg.encode('utf-8'), mavsim_server)
sent = send_sock.sendto(msg.encode('utf-8'), mavsim_server)


