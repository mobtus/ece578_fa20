from matplotlib import pyplot as plt 
import numpy as np

with open("20201001.as2types.txt", "r") as f:

    TA = 0
    Content = 0 
    Enterprise = 0    

    for line in f: 
       if line[0] == '#':        
           continue
       else:
           b = line.split("|")
        
           if (b[2] == "Transit/Access\n"):
               TA += 1
            
           elif (b[2] == "Content\n"):
                Content +=1
        
           elif (b[2] == "Enterprise\n"):
                Enterprise +=1
        
    print("Transit/Access = ", TA)
    print("Content = ", Content)
    print("Enterprise = ", Enterprise)
        
Total  = TA + Content + Enterprise
print("Total = ", Total)
    
Titles = ['Transit/Access', 'Content', 'Enterprise']

data = [TA/Total, Content/Total, Enterprise/Total]

def func(pct, allvalues): 
    absolute = int(pct / 100.*np.sum(allvalues)) 
    return "{:.1f}%\n".format(pct, absolute) 

fig, ax = plt.subplots(figsize =(10, 7)) 
wedges, texts, autotexts = ax.pie(data, autopct = lambda pct: func(pct, data))

ax.legend(wedges, Titles,
          loc ="center left", 
          bbox_to_anchor =(1, 0, 0.5, 1)) 

plt.setp(autotexts, size = 8, weight ="bold")
plt.show()


f.close()