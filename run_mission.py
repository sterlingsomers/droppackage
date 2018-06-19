import sys
import socket
import struct

#import actr
import threading
import yaml
import uuid
import subprocess



uuid = uuid.uuid4().hex
print("uuid", uuid)

msgs = [['SIM','NEW','godiland-base', uuid], ['FLIGHT', 'ARM'], ['FLIGHT', 'MS_LOAD_PAYLOAD', 0, 'food'],
        ['FLIGHT', 'AUTO_TAKEOFF'],['FLIGHT', 'MS_NO_ACTION'],['FLIGHT', 'MS_NO_ACTION'],
        ['FLIGHT', 'MS_NO_ACTION'],['FLIGHT', 'MS_NO_ACTION'],['FLIGHT', 'MS_NO_ACTION'],
        ['FLIGHT', 'MS_NO_ACTION'],['FLIGHT', 'MS_NO_ACTION'],['FLIGHT', 'MS_NO_ACTION'],
        ['FLIGHT', 'FLY_TO', 485, 29, 3],['FLIGHT', 'MS_NO_ACTION'],['FLIGHT', 'MS_NO_ACTION'],
        ['FLIGHT', 'MS_NO_ACTION'],['FLIGHT', 'MS_NO_ACTION'],['FLIGHT', 'MS_NO_ACTION']]

def ListToFormattedString(alist):
    # Each item is right-adjusted, width=3
    formatted_list = ["'{}'" if isinstance(i,str) else "{}" for i in alist]
    #print(formatted_list)
    s = '(' + ','.join(formatted_list) +')'
    return s.format(*alist)

mavsim_server = ('127.0.0.1', 32786)
send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

for msg in msgs:
    msg = ListToFormattedString(msg)
    print("sending", msg)
    sent = send_sock.sendto(msg.encode('utf-8'),mavsim_server)
    data, server = send_sock.recvfrom(1024)
    print(data.decode('utf-8'))

print("take-off procedure complete.")
subprocess.run(["docker", "exec", "q-agent", "python3", "main.py", "--env-id", "apl-nav-godiland-v0", "--drop_payload_agent",
     "--qfunction", "./q_functions/qf_v0.qf"])

# mavsim_server = ('127.0.0.1', 32786)
# send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# msg = '(\'SIM\', \'NEW\', \'godiland-base\', \'{}\')'.format(uuid)
# sent = send_sock.sendto(msg.encode('utf-8'), mavsim_server)
# msg = '(\'FLIGHT\', \'ARM\')'
# sent = send_sock.sendto(msg.encode('utf-8'), mavsim_server)
# msg = '(\'FLIGHT\', \'MS_LOAD_PAYLOAD\', 0, \'food\')'
# sent = send_sock.sendto(msg.encode('utf-8'), mavsim_server)
# msg = '(\'FLIGHT\',\'AUTO_TAKEOFF\')'
# sent = send_sock.sendto(msg.encode('utf-8'), mavsim_server)
# msg = '(\'FLIGHT\',\'MS_NO_ACTION\')'
# sent = send_sock.sendto(msg.encode('utf-8'), mavsim_server)
# sent = send_sock.sendto(msg.encode('utf-8'), mavsim_server)
# sent = send_sock.sendto(msg.encode('utf-8'), mavsim_server)
# sent = send_sock.sendto(msg.encode('utf-8'), mavsim_server)
# sent = send_sock.sendto(msg.encode('utf-8'), mavsim_server)
# sent = send_sock.sendto(msg.encode('utf-8'), mavsim_server)
# sent = send_sock.sendto(msg.encode('utf-8'), mavsim_server)
# sent = send_sock.sendto(msg.encode('utf-8'), mavsim_server)
# sent = send_sock.sendto(msg.encode('utf-8'), mavsim_server)
# sent = send_sock.sendto(msg.encode('utf-8'), mavsim_server)
# msg = '(\'FLIGHT\', \'FLY_TO\', 485, 29, 3)'
# sent = send_sock.sendto(msg.encode('utf-8'), mavsim_server)
# msg = '(\'FLIGHT\',\'MS_NO_ACTION\')'
# sent = send_sock.sendto(msg.encode('utf-8'), mavsim_server)
# sent = send_sock.sendto(msg.encode('utf-8'), mavsim_server)
# sent = send_sock.sendto(msg.encode('utf-8'), mavsim_server)
# sent = send_sock.sendto(msg.encode('utf-8'), mavsim_server)
# sent = send_sock.sendto(msg.encode('utf-8'), mavsim_server)
# sent = send_sock.sendto(msg.encode('utf-8'), mavsim_server)


