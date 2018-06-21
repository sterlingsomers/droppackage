import psycopg2
import pickle
import numpy as np
import ast

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

list_of_chunks_as_lists = []
for mission_uuid in database:
    for step in database[mission_uuid]:
        chunk = []
        #print(step['observation'])
        observation = step['observation'].strip('[]').split(' ')
        observation = np.asarray(observation, dtype=np.float64, order='C')


        action = step['action']
        environment = step['environment']
        reward = step['reward']







