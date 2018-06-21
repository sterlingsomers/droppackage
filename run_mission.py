import sys
import socket
import struct

#import actr
import threading
import yaml
import uuid
import subprocess
import pickle


def ListToFormattedString(alist):
    # Each item is right-adjusted, width=3
    # modified from: https: // stackoverflow.com / questions / 7568627 / using - python - string - formatting - with-lists
    formatted_list = ["'{}'" if isinstance(i, str) else "{}" for i in alist]
    # print(formatted_list)
    s = '(' + ','.join(formatted_list) + ')'
    return s.format(*alist)



uuids = []

for i in range(10):
    hiker_positions = [[70,50],[90,50],[110,50],[130,50]]
    mission_uuid = uuid.uuid4().hex
    session_uuid = uuid.uuid4().hex
    instance_uuid = uuid.uuid4().hex
    uuids.append({'mission':mission_uuid,'session':session_uuid,'instance':instance_uuid})
    #print("uuid", auuid)
    msgs = [['SIM', 'INSTANCE', 'instance_{}'.format(instance_uuid)],
            ['SIM', 'SESSION', 'session_{}'.format(session_uuid)],
            ['SIM', 'PILOT', 'ACTR_TEST'],
            ['SIM', 'CLOSE', 'unclosed'],['SIM', 'NEW', 'godiland-base', mission_uuid], ['FLIGHT', 'ARM'], ['FLIGHT', 'MS_LOAD_PAYLOAD', 0, 'food'],
            ['FLIGHT', 'AUTO_TAKEOFF'],['FLIGHT', 'MS_NO_ACTION'],['FLIGHT', 'MS_NO_ACTION'],
            ['FLIGHT', 'MS_NO_ACTION'],['FLIGHT', 'MS_NO_ACTION'],['FLIGHT', 'MS_NO_ACTION'],
            ['FLIGHT', 'MS_NO_ACTION'],['FLIGHT', 'MS_NO_ACTION'],['FLIGHT', 'MS_NO_ACTION'],
            ['FLIGHT', 'FLY_TO', 485, 29, 3],['FLIGHT', 'MS_NO_ACTION'],['FLIGHT', 'MS_NO_ACTION'],
            ['FLIGHT', 'MS_NO_ACTION'],['FLIGHT', 'MS_NO_ACTION'],['FLIGHT', 'MS_NO_ACTION']]



    mavsim_server = ('127.0.0.1', 32786)
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    for msg in msgs:
        msg = ListToFormattedString(msg)
        print("sending", msg)
        sent = send_sock.sendto(msg.encode('utf-8'),mavsim_server)
        data, server = send_sock.recvfrom(1024)
        print(data.decode('utf-8'))

    print("take-off procedure complete.")

    print("starting the q-learner.")

    subprocess.run(["docker", "exec", "q-agent", "python3", "main.py", "--env-id", "apl-nav-godiland-v0", "--drop_payload_agent",
         "--qfunction", "./q_functions/qf_v0.qf"])

    print("DONE.")
    print("reseting.")
    msg = "('{}', '{}', '{}')".format('SIM', 'CLOSE', mission_uuid)
    #print(sending, msg)
    sent = send_sock.sendto(msg.encode('utf-8'),mavsim_server)
    data, server = send_sock.recvfrom(1024)
    print(data.decode('utf-8'))

print("compelete.")
print(uuids)

with open('110050.p', 'wb') as handle:
    pickle.dump(uuids, handle)

print("uuids pickled as 110050.p")
