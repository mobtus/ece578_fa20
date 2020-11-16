from matplotlib import pyplot as plt 
import numpy as np
import pandas as pd

def findEnterprise(data):
    nonEnterprise = np.empty(0)
    enterprise_list = np.empty(0)
    
    for line in data:
        if int(line[2]) == -1:  #P2C
           if int(line[0]) not in nonEnterprise:
               nonEnterprise = np.append(nonEnterprise, int(line[0]))
               
        else:    #P2P
           if int(line[0]) not in nonEnterprise:
               nonEnterprise = np.append(nonEnterprise, int(line[0]))
           if int(line[1]) not in nonEnterprise:
               nonEnterprise = np.append(nonEnterprise, int(line[1]))
    
    for line in data:           
        if int(line[2]) == -1:  #P2C
            if int(line[1]) not in nonEnterprise:
                enterprise_list = np.append(enterprise_list, int(line[1]))
                   
    return enterprise_list

def findContent(data):
    providers = np.empty(0)
    content_list = np.empty(0)
    list_of_peers = np.empty(0)
    
    for line in data:
        if line[2] == 0:  #P2P
            if line[0] not in list_of_peers:    #build list of AS's with at least one peer
               list_of_peers = np.append(list_of_peers, line[0])
            if line[1] not in list_of_peers:
               list_of_peers = np.append(list_of_peers, line[1])
               
        else:   #P2C
            if line[0] not in providers:
                providers = np.append(providers, line[0])
               
    for line in data:
        if line[2] == -1:
            if (line[1] not in providers) and (line[1] in list_of_peers):
                content_list = np.append(content_list, line[1])
            
    return content_list

def findTransits(data):
    transits = np.empty(0)
    
    for line in data:
        if line[2] == -1:
            if line[0] not in transits:
                transits = np.append(transits, line[0])
                
    return transits

def func(pct, allvalues): 
    absolute = int(pct / 100.*np.sum(allvalues)) 
    return "{:.1f}%\n".format(pct, absolute) 

df = np.genfromtxt("20201001.as-rel2.txt", delimiter='|', dtype=int)
enterprise = findEnterprise(df)
content = findContent(df)
transits = findTransits(df)

data = np.array([enterprise.shape[0], content.shape[0], transits.shape[0]])
data = data/np.sum(data)    #normalize
Titles = ['Enterprise', 'Content', 'Transit']

fig, ax = plt.subplots(figsize =(10, 7)) 
wedges, texts, autotexts = ax.pie(data, autopct = lambda pct: func(pct, data))

ax.legend(wedges, Titles,
          loc ="center left", 
          bbox_to_anchor =(1, 0, 0.5, 1)) 

plt.setp(autotexts, size = 8, weight ="bold")
plt.show()