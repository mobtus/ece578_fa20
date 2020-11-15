import os
import fileinput
import matplotlib.pyplot as plt 
# import numpy as np c
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
for key in sorted(ipspaces):
    #print(str(key) + " : " + str(ipspaces[key]))
    if ipspaces[key] > 2000000:
        numbig += 1

print("Number of AS's with large IP spaces: " + str(numbig))

# to do: bin the entries, make histogram
# 🤷‍♀️🤷‍♀️🤷‍♀️🤷‍♀️🤷‍♀️