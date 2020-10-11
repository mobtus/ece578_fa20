from enum import Enum

class channelStatus(Enum):
    IDLE    = 'idle'    # channel is currently idle
    RECV    = 'recv'    # channel is currently receiving data
    #PREACK  = 'preack'  # channel is waiting for SIFS to send ACK
    ACK     = 'ack'     # channel is sending ACK
    CTS     = 'cts'     # channel is sending CTS
    SIFS    = 'sifs'    # channel is busy in SIFS
    RTSWAIT = 'rtswait' # channel is receiving RTS

class Channel():

    ### constructor
    def __init__(self,
            useCarrierSense,
            sifsLength,
            ctsLength,
            ackLength,
            rtsLength):
        self.status = channelStatus.IDLE
        self.currDuration = 0
        self.sifsDuration = sifsLength
        self.ctsDuration = ctsLength
        self.ackDuration = ackLength
        self.rtsDuration = rtsLength
        self.carrierSense = useCarrierSense     # true if using carrier sensing (RTS/CTS handshake)
        self.waitingData = False
        self.users = list()                     # list of users to determine collision if multiple access at once
        self.slotsOwned = dict()

    ### dtor
    def __del__(self):
        print("Destroying Channel")

    ### get channel status
    def getStatus(self):
        return self.status

    ### station wants to acquire channel
    def acquire(self, stationName):
        print("Channel added user: " + str(stationName))
        self.users.append(stationName)

        # add station to record of how many slots in use per station
        if stationName not in self.slotsOwned:
            self.slotsOwned[stationName] = 0

    ### station forfeits channel use (when finished sending + SIFS)
    def forfeit(self, stationName):
        if stationName in self.users:
            print("Channel removed user: " + str(stationName))
            self.users.remove(stationName)

    def printOwnership(self):
        for user in self.slotsOwned:
            print("Channel ownership: " + user + " - " + str(self.slotsOwned[user]) + " slots")

    def update(self):

        nextState = self.status
        # handle idle state
        if self.status is channelStatus.IDLE and len(self.users) == 1 and self.carrierSense is False:
            # only 1 user so he gets the channel
            print("Channel receiving data!")
            nextState = channelStatus.RECV
        elif self.status is channelStatus.IDLE and len(self.users) == 1 and self.carrierSense is True:
            print("Channel receiving RTS!")
            nextState = channelStatus.RTSWAIT

        # handle recieve state
        elif self.status is channelStatus.RECV and len(self.users) == 0:
            # receive is complete since user has forfeited channel use
            nextState = channelStatus.ACK

        elif self.status is channelStatus.RECV and len(self.users) == 1:
            # update slots owned dictionary
            self.slotsOwned[self.users[0]] += 1

        # ack state
        elif self.status is channelStatus.ACK:
            self.currDuration += 1
            if self.currDuration == self.ackDuration:
                # done sending ACK
                self.waitingData = False
                nextState = channelStatus.IDLE
                print("Channel back to IDLE.")
                self.currDuration = 0

        #################################################
        ### VCS only states below!

        # wait for RTS
        elif self.status is channelStatus.RTSWAIT:
            self.currDuration += 1
            if self.currDuration == self.rtsDuration:
                nextState = channelStatus.SIFS
                self.currDuration = 0

        # sifs state
        elif self.status is channelStatus.SIFS:
            self.currDuration += 1
            if self.currDuration == self.sifsDuration:
                self.currDuration = 0
                if self.waitingData is False:
                    nextState = channelStatus.CTS
                else:
                    print("Channel receiving data!")
                    nextState = channelStatus.RECV

        elif self.status is channelStatus.CTS:
            self.currDuration += 1
            if self.currDuration == self.ctsDuration:
                self.currDuration = 0
                self.waitingData = True
                nextState = channelStatus.SIFS

        self.status = nextState