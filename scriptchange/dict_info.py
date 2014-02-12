# Copyright Colin O'Flynn 2013-2014
# Distributed under MIT License
#



import pickle

data = pickle.load(open('partial-dict.p'))

#print len(data['base'])

for t in data['values']:
    for j in data['values'][t]:
        print "%04x "%j[0],
    print ""
