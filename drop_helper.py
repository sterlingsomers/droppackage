import actr
import pickle
import json
import numpy as np
import random
from itertools import zip_longest




EPS = 10e-4
file_names = ['allchunks_v0.chunks','allchunks_v1.chunks']
chunk_lists = [] #the combined lists in the pickled files
chunks = [] #the chunks will load here (want to make sure same # from each file)
feature_values = {} #the content of chunks stored as feature:[val1,val2,...,valn]

for file_name in file_names:
    chunk_lists.append(pickle.load(open(file_name, 'rb')))

#Find the smallest list of chunks, add those chunks to chunk_list
#Then add, randomly, the same number of instances from the other lists

min_length = min([len(x) for x in chunk_lists])
for chunk_list in chunk_lists:
    random.shuffle(chunk_lists)
    chunks.extend(chunk_list[:min_length])

#now go through those, and make the feature_values
#need to go through each chunk by 2s (slot, value)
#from https://stackoverflow.com/questions/2990121/how-do-i-loop-through-a-list-by-twos
def grouper(n, iterable, fillvalue=None):
    "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)

#chunks = [['isa','decision','value1',['value1',1.5],'output',['output',1],'value2',['value2',1]],
#         ['isa','decision','value1',['value1',0],'output',['output',0],'value2',['value2',0]],
#          ['isa', 'decision', 'value1', ['value1', 1], 'output', ['output', 1], 'value2', ['value2', 1]]]
#chunks = chunks[0:5]
for chunk in chunks:
    print(chunk)
    for slot, value in grouper(2, chunk):
        print('slot',slot,'value',value,'features',feature_values)
        if not slot in feature_values:
            feature_values[slot] = []
        feature_values[slot].append(value)

#do the chunks need to change format?
#they should be slot:[slot, value]



print("")

def access_by_key(key, list):
    '''Assumes key,vallue pairs and returns the value'''
    if not key in list:
        raise KeyError("Key not in list")

    return list[list.index(key)+1]

def compute_S(blend_trace, keys_list,result_factors):
    '''For blend_trace @ time'''
    #probablities
    probs = [x[3] for x in access_by_key('MAGNITUDES',access_by_key('SLOT-DETAILS',blend_trace[0][1])[0][1])]
    #feature values in probe
    FKs = [access_by_key(key.upper(),access_by_key('RESULT-CHUNK',blend_trace[0][1])) for key in keys_list]
    #FKs is fucked.

    chunk_names = [x[0] for x in access_by_key('CHUNKS', blend_trace[0][1])]

    #Fs is all the F values (may or may not be needed for tss)
    #They are organized by chunk, same order as probs
    vjks = []
    for name in chunk_names:
        chunk_fs = []
        for key in keys_list:
            chunk_fs.append(actr.chunk_slot_value(name,key))
        vjks.append(chunk_fs)

    #tss is a list of all the to_sum
    #each to_sum is Pj x dSim(Fs,vjk)/dFk
    #therefore, will depend on your similarity equation
    #in this case, we need max/min of the features because we use them to normalize
    #max_val = max(map(max, zip(*feature_sets)))
    #min_val = min(map(min, zip(*feature_sets)))
    #it's a bit more complex in drone case
    #I know its' 25 and 0 though
    #max_val = 25
    #min_val = 0

    #print(FKs, keys_list)

    #n = max_val - min_val
    #n = max_val
    #instead, build an n-list
    #June 26
    n = []
    for x in keys_list:
        #print("xxxxx", x)
        feature_list = feature_values[x]
        y = [p[1] for p in feature_list]
        n.append(max(y)+EPS)



    #    print('ffff',feature_values[x][1])
    #n = [max(feature_values[x][1]) for x in keys_list]



    #n = 1
    #this case the derivative is:
    #           Fk > vjk -> -1/n
    #           Fk = vjk -> 0
    #           Fk < vjk -> 1/n
    #compute Tss
    #there should be one for each feature
    #you subtract the sum of each according to (7)
    tss = {}
    ts2 = []
    for i in range(len(FKs)):
        if not i in tss:
            tss[i] = []
        for j in range(len(probs)):
            #print("####",FKs[i], vjks[j][i])
            if FKs[i] > vjks[j][i][1]:
                #print("NNNNNN",n,n[i])
                dSim = -1/n[i]
            elif FKs[i] == vjks[j][i][1]:
                dSim = 0
            else:
                dSim = 1/n[i]
            tss[i].append(probs[j] * dSim)
        ts2.append(sum(tss[i]))
        print(ts2)

    #vios
    viosList = []
    for xx in result_factors:
        viosList.append([actr.chunk_slot_value(x,xx) for x in chunk_names])

    #viosList.append([actr.chunk_slot_value(x,'pos_x_lon') for x in chunk_names])
    #viosList.append([actr.chunk_slot_value(x,'pos_y_lat') for x in chunk_names])
    #viosList.append([actr.chunk_slot_value(x,'distance_to_hiker') for x in chunk_names])


    #viosList.append([actr.chunk_slot_value(x, 'water') for x in chunk_names])
    #viosList.append([actr.chunk_slot_value(x, 'firstaid') for x in chunk_names])
    #compute (7)
    rturn = []
    for vios in viosList:
        print('vios',vios)
        results = []
        for i in range(len(FKs)):
            print("FK",FKs[i])
            tmp = 0
            sub = []
            for j in range(len(probs)):
                #print('vjksJ',vjks[j])
                print('vjksJI',vjks[j][i])
                if FKs[i] > vjks[j][i][1]:
                    dSim = -1/n[i]
                elif FKs[i] == vjks[j][i][1]:
                    dSim = 0
                else:
                    dSim = 1/n[i]
                tmp = probs[j] * (dSim - ts2[i]) * vios[j][1]#sum(tss[i])) * vios[j]
                print('tmp', tmp, 'probs', probs[j], 'dSim', dSim, 'ts2', ts2[i], 'vios',vios[j][1])
                sub.append(tmp)
            results.append(sub)

        print("compute S complete")
        rturn.append(results)
    return rturn



def similarity(val1, val2):
    '''Linear tranformation, abslute difference'''
    print("similarity", val1, val2)
    slot = val2[0].lower()
    val2 = val2[1]
    print('val1',val1,'val2',val2)
    if val1 == None:
        return None
    if val1 == 0:
        print('val1 is zero')
    if val2 == 0:
        print('val2 is zero')
    #max_val = max(map(max, zip(*feature_sets)))
    #min_val = min(map(min, zip(*feature_sets)))
    #again, max and min are more complicated
    values = [x[1] for x in feature_values[slot]]
    min_val = min(values)
    max_val = max(values)
    max_val += EPS
    print('min', min_val, 'max', max_val)
    #print("max,min,val1,val2",max_val,min_val,val1,val2)
    val1_t = (((val1 - min_val) * (0 + 1)) / (max_val - min_val)) + 0
    val2_t = (((val2 - min_val) * (0 + 1)) / (max_val - min_val)) + 0
    #print("val1_t,val2_t", val1_t, val2_t)
    #print("sim returning", abs(val1_t - val2_t) * -1)
    #print("sim returning", ((val1_t - val2_t)**2) * - 1)
    #return float(((val1_t - val2_t)**2) * - 1)
    #return abs(val1_t - val2_t) * - 1
    #return 0
    #print("sim returning", abs(val1_t - val2_t) * - 1)
    #return abs(val1_t - val2_t) * -1
    print("sim returning", (abs(val1 - val2) * - 1)/max_val)
    return (abs(val1 - val2) * - 1)/max_val

    print("sim returning", abs(val1 - val2) / (max_val - min_val) * - 1)
    return abs(val1 - val2) / (max_val - min_val) * - 1


actr.add_command('similarity_function',similarity)
actr.load_act_r_model("/Users/paulsomers/COGLE/droppackage/droppackage/drop.lisp")
actr.record_history("blending-trace")



#add the chunks to actr
for chunk in chunks:
    actr.add_dm(chunk)


probe = ['isa', 'observation', 'altitude', 2.0, 'drop_payload', 1, 'trees', 25, 'grass', 0, 'altitude_0', 25, 'altitude_1', 25, 'altitude_2', 0, 'altitude_3', 0]
#probe = ['isa', 'observation', 'value1', 0.5, 'something', 0]

probe = [x[1] if isinstance(x,list) else x for x in probe]
#chunk = "({} {} {} {})".format('isa', 'observation', 'true', 'false')
chunk = actr.define_chunks(probe)
actr.schedule_simple_event_now("set-buffer-chunk", ['imaginal', chunk[0]])
print("")
actr.run(10)

print("Using chunk", probe)

d = actr.get_history_data("blending-trace")
d = json.loads(d)

asdf = actr.get_history_data("blending-times")

MP = actr.get_parameter_value(':mp')
# #get t
t = access_by_key('TEMPERATURE',d[0][1])
# #the values
# vs = [actr.chunk_slot_value(x,'value') for x in chunk_names]
#
##factors = ['trees','grass','altitude','altitude_0','altitude_1','altitude_2','altitude_3']
factors = ['trees','altitude_1','altitude_0','altitude_2','altitude_3']
result_factors = ['pos_x_lon','pos_y_lat','distance_to_hiker']
#factors = ['needsFood', 'needsWater']
##result_factors = ['pos_x_lon','pos_y_lat','distance_to_hiker']
#result_factors = ['food','water']
results = compute_S(d, factors, result_factors)#,'f3'])
for sums,result_factor in zip(results,result_factors):
    print("For", result_factor)
    for s,factor in zip(sums,factors):
        print(factor, round(MP/t * sum(s),4))

#print("actual value is", actr.chunk_slot_value('OBSERVATION0','ACTUAL'))
print("probe is", probe)
print("done")


