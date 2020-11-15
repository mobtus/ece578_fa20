import os
import fileinput
import matplotlib.pyplot as plt 
import numpy as np
from matplotlib import colors 
from matplotlib.ticker import PercentFormatter 


dirPath = os.path.dirname(__file__)
filename = os.path.abspath(os.path.join(dirPath, os.curdir,os.curdir,'routeviews-rv2-20201113-2200.pfx2as'))
# print(filename)
ipspaces = dict()
try:
    with open(filename, 'r') as routeFile:
        for line in routeFile:
            validline = line.split() # split on whitespace
            # validline[0] is ip prefix
            # validline[1] is prefix length
            # validline[2] is AS (can be multiple)
            validline[2] = validline[2].split("_")[0].split(",")[0] # get rid of multiples (from piazza question)
            if validline[2] not in ipspaces:
                ipspaces[int(validline[2])] = 2**(32-int(validline[1]))
            else:
                ipspaces[int(validline[2])] += 2**(32-int(validline[1]))

except IOError: 
    print("Error: File does not appear to exist.")

numbig = 0
ipList = np.empty(0)
for key in sorted(ipspaces):
    #print(str(key) + " : " + str(ipspaces[key]))
    ipList = np.append(ipList, ipspaces[key])
    if ipspaces[key] > 2000000:
        numbig += 1

print("Number of AS's with large IP spaces: " + str(numbig))

ipList = np.sort(ipList)
histData = dict()
keys = np.empty(0)

for x in ipList:
    if str(x) not in histData:
        histData[str(x)] = 1
        keys = np.append(keys, x)
    else:
        histData[str(x)] += 1
        
histData2 = np.empty(0)
for x in keys:
    histData2 = np.append(histData2, histData[str(x)])
    
histData3 = np.array([histData2[0] + histData2[1] + histData2[2], 
                      histData2[3] + histData2[4], 
                      histData2[5] + histData2[6],
                      histData2[7] + histData2[8],
                      histData2[9] + histData2[10],
                      histData2[11] + histData2[12],
                      histData2[13] + histData2[14],
                      histData2[15] + histData2[16],
                      histData2[17] + histData2[18],
                      histData2[19] + histData2[20]])
histData3 = histData3/np.sum(histData3)

binLabels = ['1-8', '16-32', '64-128', '256-512', '1024-2048', '4096-8192',
             '16384-32768', '65536-131072', '26144-524288', '1.04858e+06 - 2.09715e+06']
plt.bar(binLabels, histData3)
plt.show()