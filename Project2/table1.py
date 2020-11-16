from ASEntry import ASEntry
from ASEntry import linkType

import os
import fileinput
import matplotlib.pyplot as plt 
# import numpy as np c
from matplotlib import colors 
from matplotlib.ticker import PercentFormatter 




# load entries into memory

dirPath = os.path.dirname(__file__)
filename = os.path.abspath(os.path.join(dirPath, os.curdir,os.curdir,'20201001.as-rel2.txt'))
print("opening " + filename)
entrylist = list()  # contains list of AS entries from input file
try:
    with open(filename,'r') as myFile:
        for line in myFile:
            line = line.strip()
            if line[:1] == '#':
                continue
            validline = line.split('|')
            entry = ASEntry(validline[0], validline[1], int(validline[2]))
            entrylist.append(entry)
except IOError: 
    print("Error: File does not appear to exist.")

# find node degree (number of distinct links [all types] incident to the AS)
print("Finding node degrees...")
nodedegrees = dict()
for asi in entrylist:
    if asi.as1 not in nodedegrees:
        nodedegrees[asi.as1] = 1
    else:
        nodedegrees[asi.as1] += 1

iterator = 0
# for key in nodedegrees:
#     print("Degree of " + str(key) + " : " + str(nodedegrees[key]))
#     iterator += 1
#     if iterator == 20:
#         break

for key in {key1: val for key1, val in sorted(nodedegrees.items(), key = lambda ele: ele[1], reverse = True)} :
    print("Degree of " + str(key) + " : " + str(nodedegrees[key]))
    iterator += 1
    if iterator == 20:
        break

# get clique thingies
slist = list()
for key in {key1: val for key1, val in sorted(nodedegrees.items(), key = lambda ele: ele[1], reverse = True)} :
    if len(slist) == 0:
        print("added " + str(key))
        slist.append(key)
    elif len(slist) == 10:
        break
    else:
        # determine if AS is connected to all previous AS's
        print("checking " + str(key))
        found = 0
        for asi in slist:
            oldfound = found
            for asentry in entrylist:
                if int(asentry.as1) == int(asi) and int(asentry.as2) == int(key):
                    # found one, so we're good
                    print("connected via entry: " + str(asentry))
                    found += 1
                    break
                elif int(asentry.as1) == int(key) and int(asentry.as2) == int(asi):
                    # found one, so we're good
                    print("connected via entry: " + str(asentry))
                    found += 1
                    break
            if oldfound == found:
                # AS's are not connected
                print("rip not connected: " + str(key) + " and " + str(asi))
                found = 0
                break
        if found == 0:
            # mission failed but try next AS
            continue
        else:
            # success!
            print("added " + str(key))
            slist.append(key)

print(slist)

# now we have to map them :(
dirPath = os.path.dirname(__file__)
filename = os.path.abspath(os.path.join(dirPath, os.curdir,os.curdir,'20201001.as-org2info.txt'))
print("opening " + filename)
orglist = dict()  # contains list of org entries from input file
try:
    with open(filename,'r') as myFile:
        for line in myFile:
            line = line.strip()
            validline = line.split('|')
            if not validline[0].isnumeric():
                # this is an organization field (we want AS field)
                continue
            orgaut = validline[0]
            if orgaut in slist:
                orglist[orgaut] = validline[2] # org name
except IOError: 
    print("Error: File does not appear to exist.")

totaldegree = 0
for asi in slist:
    print("AS: " + str(asi) + " Degree: " + str(nodedegrees[asi]) + " Org: " + str(orglist[asi]))
    totaldegree += nodedegrees[asi]
print("Size of T1 list as total degree: " + str(totaldegree))