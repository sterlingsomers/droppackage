'''An ACT-R server to and from mavsim

IP and ports are as follows...'''


import sys
import socket
import struct

import actr
import threading
import yaml


#ACTR commands
#send commmand/function
def sendtoUDP(msg):
    #the msg has to be byte
    byte_msg = str.encode(msg)
    sent = sock.sendto(byte_msg, server_address)

state_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
state_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
state_address = ('127.0.0.1', 9024)
state_socket.bind(state_address)
state = {}
def read_state():
    while 1:
        data, add = state_socket.recvfrom(1024)
        data = data.decode('utf-8')
        global state
        print(data)
        state[data[:data.find('{')-1]] = yaml.load(data[data.find('{'):])
        if 'GLOBAL_POSITION_INT' in state:
            latitude = state['GLOBAL_POSITION_INT']['vy']
            longitude = state['GLOBAL_POSITION_INT']['vx']
            print("lat,lon",latitude, longitude)
            #get sensor grid
            #sock.sendto(b'(\'FLIGHT\', \'MS_QUERY_TERRAIN\', latitude,\'longitude\')', server_address)
            msg = "('FLIGHT', 'MS_QUERY_TERRAIN', {}, {})".format(latitude, longitude)
            sock.sendto(msg.encode('utf-8'), server_address)


#UDP connection to mavsim.
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('localhost', 32786)
#put myself in the multicast
#sent = sock.sendto(b'(\'TELEMETRY\', \'SET_MULTICAST\', \'ON\')', server_address)
#sent = sock.sendto(b'(\'TELEMETRY\', \'ADD_LISTENER\', \'127.0.0.1\', 9025, 0)', server_address)
#sent = sock.sendto(b'(\'TELEMETRY\', \'ADD_LISTENER\', \'docker.for.mac.localhost\', 9027, 0)', server_address)




stateThread = threading.Thread(target=read_state)
stateThread.start()





#First start ACT-R, running for however long
    #load an ACT-R model
actr.load_act_r_model("/Users/paulsomers/COGLE/droppackage/droppackage/drop.lisp")
    #add some commands
actr.add_command('send', sendtoUDP)

actrThread = threading.Thread(target=actr.run, args=[0.05])
actrThread.start()

print("ok")








