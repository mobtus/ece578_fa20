from ASEntry import ASEntry
from ASEntry import linkType

import os
import fileinput
import matplotlib.pyplot as plt 
import numpy as np
from matplotlib import colors 
from matplotlib.ticker import PercentFormatter 




# load entries into memory

dirPath = os.path.dirname(__file__)
filename = os.path.abspath(os.path.join(dirPath, os.curdir,os.curdir,'20201001.as-rel2.txt'))
print(filename)
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

degreebins = np.array([0, 0, 0, 0, 0, 0]) # 1, 2-5, 6-100, 101-200, 201-1000, 1001+
for key in nodedegrees:
    if nodedegrees[key] == 1:
        degreebins[0] += 1
    elif nodedegrees[key] <= 5:
        degreebins[1] += 1
    elif nodedegrees[key] <= 100:
        degreebins[2] += 1
    elif nodedegrees[key] <= 200:
        degreebins[3] += 1
    elif nodedegrees[key] <= 1000:
        degreebins[4] += 1
    else:
        degreebins[5] += 1
        

degreebins=degreebins/sum(degreebins)
#print(degreebins)

binLabels = ['1', '2-5', '6-100', '101-200', '201-1000', '1001+']
plt.bar(binLabels, degreebins)
plt.show()
