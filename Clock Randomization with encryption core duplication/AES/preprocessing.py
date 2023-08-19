import numpy as np

def find_concurrent(t):
    l = 1.5*np.std(t)				#threshold based on standard deviation
    o = 10					#offset to ignore init round
    concurrent = []				#list of traces with first round concurrent peaks
    split = []					#list of traces with first round split peaks
    for i in range(t.shape[0]):
        if len(np.where(np.abs(t[i,o:])>l)[0]) < 1:		#ignore traces without peaks, if any
            continue
        if len(np.where(np.abs(t[i,o:])>2*l)[0]) < 1:		#if there are no concurrent peaks
            split += [i]
            continue
        if np.where(np.abs(t[i,o:])>l)[0][0] == np.where(np.abs(t[i,o:])>2*l)[0][0]:	#if first is concurrent
            concurrent += [i]
        else: split+=[i]
    return (concurrent, split)

def synchronize_concurrent(t, concurrent):
    ctraces = []
    l = 1.5*np.std(t)
    o = 10
    for i in concurrent:			#list of indices of t with concurrent first rounds
        arr = np.where(np.abs(t[i,o:])>l)[0]	#find peaks
        a = arr[0]+o
        temp = [a]
        for j in range(1,len(arr)):
            if arr[j]+o - temp[-1] > 2:		#look for (mostly) contiguous sequences
                break
            temp += [arr[j]+o]
        ind = temp[int(len(temp)/2)]		#center interval on middle index
        ctraces += [t[i,ind-10:ind+40]]		#we use a 50 point interval around leakage point
    return np.array(ctraces)

def synchronize_and_merge(t, split):
    mtraces = []
    inds = []	#because we may skip a trace where the next comment is, we save inds to not use wrong plaintexts
    l = 1.5*np.std(t)
    o = 10
    counter = 0
    for i in split:
        arr = np.where(np.abs(t[i,o:])>l)[0]
        if len(arr)<10:				#if for some reason not all peaks exist...
            continue
        inds += [i]
        a = arr[0]+o
        temp = [a]
        for j in range(1,len(arr)):
            if arr[j]+o - temp[-1] > 2:
                if counter == 0:
                    counter += 1
                    ind2 = temp[int(len(temp)/2)]		#we need two index values to merge
                    temp = [arr[j]+o]
                    continue
                else:
                    counter = 0
                break
            temp += [arr[j]+o]
        ind = temp[int(len(temp)/2)]				#second index value
        mtraces += [t[i,ind-10:ind+40] + t[i,ind2-10:ind2+40]]
        return (np.array(mtraces), inds)			#inds can be used to select the plaintexts and keys used

#loading files (placeholder names)
folder = "traces/"
t = np.load(folder+"traces.npy")
p = np.load(folder+"pts.npy")
c = np.load(folder+"cts.npy")
k = np.load(folder+"keys.npy")

#find concurrent peaks
concurrent, split = find_concurrent(t)

#synchronize concurrent peaks
tc = synchronize_concurrent(t, concurrent)
pc = p[concurrent]
cc = c[concurrent]
kc = k[concurrent]

#synchronize and merge split peaks
tm, inds = synchronize_and_merge(t, split)
pm = p[inds]
cm = c[inds]
km = k[inds]

#save the files here if you want (placeholder names)
pref = "filename"
pref2 = "filename2"
np.save(pref+"_traces.npy", tc)
np.save(pref+"_pts.npy", pc)
np.save(pref+"_cts.npy", cc)
np.save(pref+"_keys.npy", kc)
np.save(pref2+"_traces.npy", tm)
np.save(pref2+"_pts.npy", pm)
np.save(pref2+"_cts.npy", cm)
np.save(pref2+"_keys.npy", km)