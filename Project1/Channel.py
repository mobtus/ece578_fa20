from enum import Enum

class channelStatus(Enum):
    IDLE    = 'idle'    # channel is currently idle
    RECV    = 'recv'    # channel is currently receiving data
    #PREACK  = 'preack'  # channel is waiting for SIFS to send ACK
    ACK     = 'ack'     # channel is sending ACK
    CTS     = 'cts'     # channel is sending CTS

class Channel():

    ### constructor
    def __init__(self,
            useCarrierSense,
            ackLength):
        self.status = channelStatus.IDLE
        self.currDuration = 0
        self.ackDuration = ackLength
        self.carrierSense = useCarrierSense     # true if using carrier sensing (RTS/CTS handshake)
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
        self.users.append(stationName)

        # add station to record of how many slots in use per station
        if stationName not in self.slotsOwned:
            self.slotsOwned[stationName] = 0

    ### station forfeits channel use (when finished sending + SIFS)
    def forfeit(self, stationName):
        if stationName in self.users:
            print("Channel removed user!")
            self.users.remove(stationName)

    def update(self):

        nextState = self.status
        # handle idle state
        if self.status is channelStatus.IDLE and len(self.users) == 1:
            # only 1 user so he gets the channel
            print("Channel receiving data!")
            nextState = channelStatus.RECV

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
                nextState = channelStatus.IDLE
                print("Channel back to IDLE.")
                self.currDuration = 0

        self.status = nextState