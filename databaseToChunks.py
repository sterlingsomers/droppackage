import psycopg2
import pickle
import numpy as np
import ast
import json
import yaml
import mapquery

con = psycopg2.connect(dbname='apm_missions',user='postgres',password='sterling',host='localhost',port=32768)
cur = con.cursor()
filenumber = '070050'
uuid_list = pickle.load(open(filenumber + '.p', "rb"))

database = {}
#uuid_list = [uuid_list[0]]
for uuids in uuid_list:
    mission_uuid = uuids['mission']
    cur.execute("SELECT mavsim_openlog.* FROM flights JOIN mavsim_openlog ON "
                 "flights.simulation_session_uuid = mavsim_openlog.simulation_session_uuid WHERE"
                 " flights.uuid='{}' ORDER BY mavsim_openlog.id;".format(mission_uuid))

    line = cur.fetchone()
    previous_line = ''
    step = {}
    while line is not None:
        #print(line)
        while 'REWARD' not in line:

            if "RAW_OBSERVATIONS" in line:
                step['observation'] = line[line.index('RAW_OBSERVATIONS') + 1]
            if "ENV_STEP_INFO" in  line:
                step['environment'] = line[line.index('ENV_STEP_INFO') + 1]
            if "AGENT_ACTIONS" in line:
                step['action'] = line[line.index('AGENT_ACTIONS') + 1]
            line = cur.fetchone()
        if "REWARD" in line:
            step['reward'] = line[line.index('REWARD') + 1]
        #previous_line = line
        if not mission_uuid in database:
            database[mission_uuid] = []
        database[mission_uuid].append(step.copy())
        line = cur.fetchone()
        #break

with open(filenumber + '.dict', 'wb') as handle:
    pickle.dump(database, handle)

print("pickled the database to dictionary as {}.dict".format(filenumber))

def step_by_step():
    '''a state-by-state represenation building (incomplete...)'''
    dict_of_chunks_as_lists = {}
    for mission_uuid in database:
        if not mission_uuid in dict_of_chunks_as_lists:
            dict_of_chunks_as_lists[mission_uuid] = []
        for step in database[mission_uuid]:
            chunk = []
            #print(step['observation'])
            observation = step['observation'].strip('[]').split(' ')
            observation = np.asarray(observation, dtype=np.float64, order='C')
            #print(observation)
            chunk.append('pos_x_lon')
            chunk.append(observation[0])
            chunk.append('pos_y_lat')
            chunk.append(observation[1])
            chunk.append('altitude')
            chunk.append(observation[2])
            current_altidude = int(observation[2])
            environment = step['environment']
            env = yaml.load(environment)
            #print(env['distance_to_target'])
            chunk.append('distance_to_hiker')
            chunk.append(env['distance_to_target'])
            #print(env)
            action = step['action']
            #print(action)
            if 'DROP_PAYLOAD' in action:
                chunk.append('altitude_change')
                chunk.append(head_to_values[2] - current_altidude)
                chunk.append('drop_payload')
                chunk.append(1)

            elif 'HEAD_TO' in action:
                x = action[action.find('HEAD_TO,')+9:action.find(')')]
                head_to_values = [int(n) for n in x.split(',')]
                chunk.append('altitude_change')
                chunk.append(head_to_values[2] - current_altidude)
                chunk.append('drop_payload')
                chunk.append(0)




            else:
                chunk.append('altitude_change')
                chunk.append(0)
                chunk.append('drop_payload')
                chunk.append(0)

            #print(chunk)
            dict_of_chunks_as_lists[mission_uuid].append(chunk)

    return dict_of_chunks_as_lists






def chunk_by_environment_and_drop():
    '''One chunk per mission. Where it dropped, plus environment near hiker'''

    #First get the last observation from each mission
    #get all the step-by-step chunks, and get the last one from each mission
    dict_of_chunks = step_by_step()
    #print(dict_of_chunks)
    chunks = [dict_of_chunks[chunks][-1] for chunks in dict_of_chunks]





chunk_by_environment_and_drop()