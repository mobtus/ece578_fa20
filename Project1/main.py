from Station import Station
from Station import stationStatus
from Channel import Channel
from Channel import channelStatus


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
simTime = 1

# slot duration in micro seconds
slotDuration = 10
uS_to_S = 1e6

numSlots = int((uS_to_S / slotDuration) * simTime)

print("Number of slots: " + str(numSlots) )
# print(str(type(lambdaA)))


# to do: calculate frame arrival slots based on random uniformly distributed values

# frame arrival slots
xa = [100, 256, 334, 500, 715, 999]
xc = [100, 256, 334, 500, 715, 999]
#xc = [130, 246, 404, 500, 820, 972]
#xa = [100]
#xc = [100]

# initialize channel and stations
channel = Channel(False, ackDuration)
stationA = Station("A", channel)
stationC = Station("C", channel)

stationA.setArrivals(xa)
stationC.setArrivals(xc)

stationA.setParams(difsDuration, sifsDuration, ackDuration, rtsDuration, ctsDuration, contentionWindow, contentionWindowMax, dataFrameSizeSlots)
stationC.setParams(difsDuration, sifsDuration, ackDuration, rtsDuration, ctsDuration, contentionWindow, contentionWindowMax, dataFrameSizeSlots)

# main loop
for i in range(0, numSlots):
    stationA.update(i)
    stationC.update(i)
    channel.update()

# to do: final data calculations