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



# use carrier sensing?
useCarrierSense = True

# which scenario are we running?
stationsListening = True


def calc_arriv_time(input_lambda):

    points = input_lambda * simTime

    # uniformly distributed values
    ua = list()
    uc = list()
    for i in range(0, points):
        ua.append((random.randint(0, 100000) / 100000))
        uc.append((random.randint(0, 100000) / 100000))

    # uniformly distributed values converted into exponentially distributed values 
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

    for i in range(0, len(xa)):
        xa[i] = math.ceil(xa[i])
        
    for i in range(0, len(xc)):
        xc[i] = math.ceil(xc[i])

    for i in range(1, len(xa)):
        xa[i] = xa[i] + xa[i-1]
        
    for i in range(1, len(xc)):
        xc[i] = xc[i] + xc[i-1]
    
    return [xa, xc]


# frame arrival slots
xa_arrivals = list()
xc_arrivals = list()

[xa_arrivals, xc_arrivals] = calc_arriv_time(2000)


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

# final data calculations

T_a = (stationA.successes * dataFrameSizeBytes) * 8 / simTime
T_c = (stationC.successes * dataFrameSizeBytes) * 8 / simTime
print("Transmission rate for station " + stationA.name + ": " + str(T_a))
print("Transmission rate for station " + stationC.name + ": " + str(T_c))

channel.printOwnership()
print("Fairness Index:" , (channel.slotsOwned['A'] / channel.slotsOwned['C']))