import psycopg2
import pickle
import numpy as np
import ast
import json
import yaml
import mapquery

#To run this, make sure you have the file number and set the file number and arguments to chunk_by_environment appropriately
#70, 50 --> 070050 and
#also need a mission started in mavsim -> just go to exigisi, press new, and accept default is fine.

con = psycopg2.connect(dbname='apm_missions',user='postgres',password='sterling',host='localhost',port=32768)
cur = con.cursor()

hiker_positions_x = [70, 90, 110, 130, 150, 170, 190]
hiker_positions_y = [50, 70, 90, 110]
#file_name = "{}-{}.p".format(x,y)
#Todo convert this to combinations as well.

#filenumber = '150050'
#latitude, longitude = 150, 50
#uuid_list = pickle.load(open(filenumber + '.p', "rb"))

database = {}
#uuid_list = [uuid_list[0]]
for y in hiker_positions_y:
    for x in hiker_positions_x:
        file_name = "{}-{}.p".format(x, y)
        uuid_list = pickle.load(open(file_name, "rb"))
        #print(uuid_list)
        for uuids in uuid_list:
            mission_uuid = uuids['mission']
            cur.execute("SELECT mavsim_openlog.* FROM flights JOIN mavsim_openlog ON "
                         "flights.simulation_session_uuid = mavsim_openlog.simulation_session_uuid WHERE"
                         " flights.uuid='{}' ORDER BY mavsim_openlog.id;".format(mission_uuid))

            line = cur.fetchone()
            previous_line = ''
            step = {}
            while line is not None:
                #print("LINE",line)
                if 'EVENT' in line:
                    if 'CRASH' in line[3]:
                        print("craft crashed, excluding", line)
                        break
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

        with open(file_name[:-2] + '.dict', 'wb') as handle:
            pickle.dump(database, handle)
        database = {}

        #print("pickled the database to dictionary as {}.dict".format(file_name[-2] + '.dict'))

def step_by_step(database):
    '''a state-by-state represenation building (incomplete...)'''
    dict_of_chunks_as_lists = {}
    for mission_uuid in database:
        if not mission_uuid in dict_of_chunks_as_lists:
            dict_of_chunks_as_lists[mission_uuid] = []
        for step in database[mission_uuid]:
            chunk = []
            #print(step['observation'])
            #print(mission_uuid)
            observation = step['observation'].strip('[]').split(' ')
            #print('AFTERSPLIT',observation)
            try:
                observation = np.asarray(observation, dtype=np.float64, order='C')
            except:
                print("unknown error. deleting instance.")
                del dict_of_chunks_as_lists[mission_uuid]
                continue

            #print(observation)
            chunk.append('isa')
            chunk.append('drop_point')
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
                #chunk.append('altitude_change')
                #chunk.append(head_to_values[2] - current_altidude)
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






def chunk_by_environment_and_drop(lat,lon):
    '''One chunk per mission. Where it dropped, plus environment near hiker'''

    #First get the last observation from each mission
    #get all the step-by-step chunks, and get the last one from each mission
    fileName = "{}-{}.dict".format(lat,lon)
    database = pickle.load(open(fileName,"rb"))

    dict_of_chunks = step_by_step(database)
    #print(dict_of_chunks)
    chunks = [dict_of_chunks[chunks][-1] for chunks in dict_of_chunks]
    #print("CHUNKS", chunks)

    #get the area around the hiker
    area_around_hiker = mapquery.terrain_request(lat=lat,lon=lon)

    area_around_hiker = [eval(x) for x in area_around_hiker]
    #print(area_around_hiker)

    #pine_tree = 0
    terrain_features = {'trees': 0, 'grass': 0, 'altitude_0': 0, 'altitude_1': 0, 'altitude_2': 0, 'altitude_3': 0}

    for terrain in area_around_hiker:
        #print(terrain)
        if 'pine trees' in terrain or 'pine tree' in terrain:
            terrain_features['trees'] += 1
            terrain_features['altitude_1'] += 1
        if terrain[4] == 1 and 'pine trees' not in terrain and 'pine tree' not in terrain:
            terrain_features['altitude_1'] += 1
        if terrain[4] == 0 and 'grass' in terrain:
            terrain_features['grass'] += 1
            terrain_features['altitude_0'] += 1
        if terrain[4] == 0 and not 'grass' in terrain:
            terrain_features['altitude_0'] += 1



    terrain_chunk_format = []
    for key,value in terrain_features.items():

        terrain_chunk_format.append(key)
        terrain_chunk_format.append(value)


    #extend each chunk in chunks with the terrain features for that area
    return_chunks = []
    for chunk in chunks:
        chunk.extend(terrain_chunk_format)
        return_chunks.append(chunk)

    return return_chunks



#print("chunks...",chunk_by_environment_and_drop(70,50))


hiker_positions_x = [70, 90, 110, 130, 150, 170, 190]
hiker_positions_y = [50, 70, 90, 110]
allchunks = []
#file_name = "{}-{}.p".format(x,y)
for y in hiker_positions_y:
    for x in hiker_positions_x:
        allchunks.extend(chunk_by_environment_and_drop(x,y))

print(allchunks)
with open('allchunks_v0.chunks', 'wb') as handle:
    pickle.dump(allchunks,handle)

#with open(filenumber + '.chunks', 'wb') as handle:
#    pickle.dump(chunk_by_environment_and_drop(latitude,longitude), handle)
