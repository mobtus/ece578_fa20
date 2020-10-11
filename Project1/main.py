from Station import Station
from Station import stationStatus
from Channel import Channel
from Channel import channelStatus
import math
import random

##########################
# Parameters
##########################
dataFrameSizeBytes = 1500
dataFrameSizeSlots = 50

# duration in slots
sifsDuration = 1
ackDuration = 2
rtsDuration = 2
ctsDuration = 2
difsDuration = 2
contentionWindow = 4
contentionWindowMax = 1024

# rate in frames/second
lambdaA = {200, 300, 500, 1000, 2000}
lambdaC = lambdaA

# rate in Mbps
transmissionRate = 24

# sim time in seconds
simTime = 10

# slot duration in micro seconds
slotDuration = 10
uS_to_S = 1e6

numSlots = int((uS_to_S / slotDuration) * simTime)

print("Number of slots: " + str(numSlots) )

# use carrier sensing?
useCarrierSense = False

# which scenario are we running?
stationsListening = True


def calc_arriv_time(input_lambda):
    # sim_time = 10
    # print(simTime)
    points = input_lambda * simTime

    # uniformly distributed values
    #ua = np.random.uniform(low=0.0, high=1.0, size=points)
    #uc = np.random.uniform(low=0.0, high=1.0, size=points)
    ua = list()
    uc = list()
    for i in range(0, points):
        ua.append((random.randint(0, 100000) / 100000))
        uc.append((random.randint(0, 100000) / 100000))

    # print(str(ua))
    # print(str(uc))
    # return [ua, uc]
    # uniformly distributed values converted into exponentially distributed values 
    # xa = np.empty(0)
    # xc = np.empty(0)
    xa = list()
    xc = list()
    for i in ua:
        xa.append((1/input_lambda) * math.log1p(1-i))
        
    for i in uc:
        xc.append((1/input_lambda) * math.log1p(1-i))

    
                                                                                                 
    # exponentially distributed values converted to slots rounded up to neared int
    slot_duration = (slotDuration/uS_to_S)

    for i in range(0, len(xa)):
        xa[i] = xa[i]/slot_duration
    for i in range(0, len(xc)):
        xc[i] = xc[i]/slot_duration

    # print(str(xa))
    # print(str(xc))

    
    for i in range(0, len(xa)):
        xa[i] = math.ceil(xa[i])
        
    for i in range(0, len(xc)):
        xc[i] = math.ceil(xc[i])
    
    
    # slots converted into arrival time 
    # arrival_a = np.array(xa[0])
    # arrival_c = np.array(xc[0])
    
    # print(arrival_a)
        
    for i in range(1, len(xa)):
        xa[i] = xa[i] + xa[i-1]
        
    for i in range(1, len(xc)):
        xc[i] = xc[i] + xc[i-1]
    
    return [xa, xc]





# print(str(type(lambdaA)))


# to do: calculate frame arrival slots based on random uniformly distributed values

# frame arrival slots
xa_arrivals = list()
xc_arrivals = list()
# xa = [100, 256, 334, 500, 715, 999]
#xc = [100, 256, 334, 500, 715, 999]
# xc = [130, 246, 404, 500, 820, 972]
#xa = [100]
#xc = [100]

[xa_arrivals, xc_arrivals] = calc_arriv_time(1000)
# print(str(xa_arrivals))
# print(str(xc_arrivals))
# exit()


# initialize channel and stations
channel = Channel(useCarrierSense, sifsDuration, ctsDuration, ackDuration, rtsDuration)
stationA = Station("A", channel, useCarrierSense, stationsListening)
stationC = Station("C", channel, useCarrierSense, stationsListening)

stationA.setArrivals(xa_arrivals)
stationC.setArrivals(xc_arrivals)

stationA.setParams(difsDuration, sifsDuration, ackDuration, rtsDuration, ctsDuration, contentionWindow, contentionWindowMax, dataFrameSizeSlots)
stationC.setParams(difsDuration, sifsDuration, ackDuration, rtsDuration, ctsDuration, contentionWindow, contentionWindowMax, dataFrameSizeSlots)

# main loop
for i in range(0, numSlots):
    stationA.update(i)
    stationC.update(i)
    channel.update()

# to do: final data calculations