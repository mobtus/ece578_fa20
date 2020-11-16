from matplotlib import pyplot as plt 
import numpy as np
import pandas as pd

def findCustomers(df, cone_list, base_provider, temp_AS):
    customers_found = np.empty(0)
    for line in df:
        if (line[0] == temp_AS) and (line[2] == -1):   #P2C
            if line[1] not in cone_list[str(base_provider)]:
                cone_list[str(base_provider)] = np.append(cone_list[str(base_provider)], line[1])
                customers_found = np.append(customers_found, line[1])
    
    for x in customers_found:
        cone_list = findCustomers(df, cone_list, base_provider, x)
    
    return cone_list

def func(pct, allvalues): 
    absolute = int(pct / 100.*np.sum(allvalues)) 
    return "{:.1f}%\n".format(pct, absolute) 

cone_list = dict()
keys = np.empty(0)
df = np.genfromtxt("20201001.as-rel2.txt", delimiter='|', dtype=int)

for line in df:
    # if line[0] == 42:
    #     break
    if (line[2] == -1) and (str(line[0]) not in cone_list):   #P2C link and new Provider
        keys = np.append(keys, line[0])
        cone_list[str(line[0])] = np.empty(0)
        cone_list = findCustomers(df, cone_list, line[0], line[0])

with open('customer_cones.txt', 'w') as f:
    f.writelines('AS\t\t\t\t# of customers\n')
    for x in keys:
        f.writelines([str(int(x)), '\t\t\t\t', str(cone_list[str(int(x))].shape[0]), '\n'])
