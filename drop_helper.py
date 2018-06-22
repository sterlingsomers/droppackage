import actr
import pickle
import json
import numpy as np


file_names = ['070050','090050','110050','130050']
chunks = []


for file_name in file_names:
    file_chunks = pickle.load(open(file_name + '.chunks', 'rb'))
    chunks.append(file_chunks[0])


def access_by_key(key, list):
    '''Assumes key,vallue pairs and returns the value'''
    if not key in list:
        raise KeyError("Key not in list")

    return list[list.index(key)+1]

def compute_S(blend_trace, keys_list):
    '''For blend_trace @ time'''
    #probablities
    probs = [x[3] for x in access_by_key('MAGNITUDES',access_by_key('SLOT-DETAILS',blend_trace[0][1])[0][1])]
    #feature values in probe
    FKs = [access_by_key(key.upper(),access_by_key('RESULT-CHUNK',blend_trace[0][1])) for key in keys_list]
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
    max_val = 25
    min_val = 0


    n = max_val - min_val
    n = max_val
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
            if FKs[i] > vjks[j][i]:
                dSim = -1/n
            elif FKs[i] == vjks[j][i]:
                dSim = 0
            else:
                dSim = 1/n
            tss[i].append(probs[j] * dSim)
        ts2.append(sum(tss[i]))

    #vios
    viosList = []
    viosList.append([actr.chunk_slot_value(x,'pos_x_lon') for x in chunk_names])
    viosList.append([actr.chunk_slot_value(x,'pos_y_lat') for x in chunk_names])
    viosList.append([actr.chunk_slot_value(x,'distance_to_hiker') for x in chunk_names])


    #viosList.append([actr.chunk_slot_value(x, 'water') for x in chunk_names])
    #viosList.append([actr.chunk_slot_value(x, 'firstaid') for x in chunk_names])
    #compute (7)
    rturn = []
    for vios in viosList:
        results = []
        for i in range(len(FKs)):
            tmp = 0
            sub = []
            for j in range(len(probs)):
                if FKs[i] > vjks[j][i]:
                    dSim = -1/n
                elif FKs[i] == vjks[j][i]:
                    dSim = 0
                else:
                    dSim = 1/n
                tmp = probs[j] * (dSim - ts2[i]) * vios[j]#sum(tss[i])) * vios[j]
                sub.append(tmp)
            results.append(sub)

        print("compute S complete")
        rturn.append(results)
    return rturn



def similarity(val1, val2):
    '''Linear tranformation, abslute difference'''
    if val1 == None:
        return None
    #max_val = max(map(max, zip(*feature_sets)))
    #min_val = min(map(min, zip(*feature_sets)))
    #again, max and min are more complicated
    max_val = 25
    min_val = 0
    print("max,min,val1,val2",max_val,min_val,val1,val2)
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

probe = list(chunks[3])
print("probe", probe)
find = probe.index('pos_x_lon')
del probe[find+1]
del probe[find]
find = probe.index('pos_y_lat')
del probe[find+1]
del probe[find]
find = probe.index('distance_to_hiker')
del probe[find+1]
del probe[find]
probe[1] = 'observation'
probe[9] = 12
print("probe2", probe)



chunk = actr.define_chunks(probe)
actr.schedule_simple_event_now("set-buffer-chunk", ['imaginal', chunk[0]])

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
factors = ['trees','grass','altitude','altitude_0','altitude_1']
#factors = ['needsFood', 'needsWater']
result_factors = ['pos_x_lon','pos_y_lat','distance_to_hiker']
#result_factors = ['food','water']
results = compute_S(d, factors)#,'f3'])
for sums,result_factor in zip(results,result_factors):
    print("For", result_factor)
    for s,factor in zip(sums,factors):
        print(factor, MP/t * sum(s))

#print("actual value is", actr.chunk_slot_value('OBSERVATION0','ACTUAL'))
print("probe is", probe)
print("done")


