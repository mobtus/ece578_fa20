from matplotlib import pyplot as plt 
import numpy as np

with open("20201001.as-rel2.txt", "r") as f:

    # ipSpace = np.empty((0))
    ipSpace = dict()
    nodeList = np.empty(0)
    for line in f: 
       if line[0] == '#':        
           continue
       else:
           b = line.split("|")
           
           if int(b[2]) == -1:   #P2C
               if int(b[0]) not in ipSpace:
                   ipSpace[int(b[0])] = np.array(int(b[1]))
                   nodeList = np.append(nodeList, int(b[0]))
               else:
                   ipSpace[int(b[0])] = np.append(ipSpace[int(b[0])], int(b[1]))

histData = np.empty(0)
for i in nodeList:
    # print(ipSpace[i].shape)
    if ipSpace[i].shape == ():
        histData = np.append(histData, 1)
    else:
        histData = np.append(histData, ipSpace[i].shape[0])

plt.hist(histData, bins=100)
plt.show()