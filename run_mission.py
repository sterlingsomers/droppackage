import sys
import socket
import struct

#import actr
import threading
import yaml
import uuid
import subprocess
import pickle
import itertools


def ListToFormattedString(alist):
    # Each item is right-adjusted, width=3
    # modified from: https: // stackoverflow.com / questions / 7568627 / using - python - string - formatting - with-lists
    formatted_list = ["'{}'" if isinstance(i, str) else "{}" for i in alist]
    # print(formatted_list)
    s = '(' + ','.join(formatted_list) + ')'
    return s.format(*alist)



uuids = []
hiker_positions_x = [70, 90, 110, 130, 150, 170, 190]
hiker_positions_y = [50, 70, 90, 110]

combinations = list(itertools.product(hiker_positions_x,hiker_positions_y))
#sed -i 3s:.*:"  <hiker_position>190, 110</hiker_position>": /cogle/cogle-mavsim/cogle_mavsim/assets/godiland_nav_v0.xml

combinations = [[100,350],[100,450],[100,150],[384,319],[270,50],[390,50],[410,50],[430,50],[230,70],[270,70],[350,90],[430,110]]


#last_hiker_x = 25
#last_hiker_y = 33
#need to edit the xml file to those values: 25, 33

for combination in combinations:
    print("COM",combination)
    sed_command = "3s:.*:  <hiker_position>{}, {}</hiker_position>:".format(combination[0],combination[1])
    subprocess.run(["docker", "exec", "q-agent", "sed", "-i", sed_command,
                    "/cogle/cogle-mavsim/cogle_mavsim/assets/godiland_nav_v1.xml"])


    for i in range(1):

        mission_uuid = uuid.uuid4().hex
        session_uuid = uuid.uuid4().hex
        instance_uuid = uuid.uuid4().hex
        uuids.append({'mission':mission_uuid,'session':session_uuid,'instance':instance_uuid})
        #print("uuid", auuid)
        msgs = [['SIM', 'INSTANCE', 'instance_{}'.format(instance_uuid)],
                ['SIM', 'SESSION', 'session_{}'.format(session_uuid)],
                ['SIM', 'PILOT', 'ACTR_DATA'],
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


        #First edit the xml file
        #sed_command = "0,/{}/s/{}/{}/".format(last_hiker_x,last_hiker_x,x)
        #print(sed_command)
        #last_hiker_x = x
        #subprocess.run(["docker", "exec", "q-agent", "sed", "-i", sed_command, "/cogle/cogle-mavsim/cogle_mavsim/assets/godiland_nav_v0.xml"])
        #Do the same for y


        #sed - i
        #'0,/150/s/150/170/' / cogle / cogle - mavsim / cogle_mavsim / assets / godiland_nav_v0.xml

        print("starting the q-learner.")



        subprocess.run(["docker", "exec", "q-agent", "python3", "main.py", "--env-id", "apl-nav-godiland-v1", "--drop_payload_agent",
             "--qfunction", "./q_functions/qf_v1.qf"])

        print("DONE.")
        print("reseting.")
        msg = "('{}', '{}', '{}')".format('SIM', 'CLOSE', mission_uuid)
        #print(sending, msg)
        sent = send_sock.sendto(msg.encode('utf-8'),mavsim_server)
        data, server = send_sock.recvfrom(1024)
        print(data.decode('utf-8'))

        print("compelete.")
    print(uuids)

    file_name = "{}-{}.p".format(combination[0],combination[1])

    with open(file_name, 'wb') as handle:
        pickle.dump(uuids, handle)


    print("uuids pickled as", file_name)
    uuids = []

