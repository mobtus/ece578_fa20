from enum import Enum
from Channel import Channel
from Channel import channelStatus
import random

# states of a station
class stationStatus(Enum):
    IDLE        = 'idle'        # station is not doing anything at the moment
    DIFS        = 'difs'        # station is currently in DIFS
    BACKOFF     = 'backoff'     # station is currently in backoff
    SIFS        = 'sifs'        # station is currently in SIFS
    NAV         = 'nav'         # station is currently in NAV (waiting for channel to free)
    TRANSMIT    = 'transmit'    # station is currently transmitting data
    ACKWAIT     = 'ackwait'     # station is currently awaiting ACK
    RTS         = 'rts'         # station is currently sending "ready to send"
    CTSWAIT     = 'ctswait'     # station is currently awaiting CTS


# holds values and status for each station
class Station():

    ### constructor
    def __init__(self,
            stationName,
            chan,
            carrierSense,
            listening):
        self.queue = 0
        self.status = stationStatus.IDLE
        self.currDuration = 0               # duration spent in current state
        self.currACKDur = 0                 # duration spent receiving ACK (mainly for NAV state)
        self.currBackoff = 0                # duration spent in backoff
        self.difsDuration = 0
        self.sifsDuration = 0
        self.ackDuration = 0
        self.rtsDuration = 0
        self.ctsDuration = 0
        self.contWindow = 0
        self.contWZero = 0
        self.contWMax = 0
        self.backoff = 0
        self.frameSize = 0
        self.channel = chan
        self.frameArrivals = list()
        self.collisions = 0
        self.successes = 0
        self.useCarrerSense = carrierSense
        self.isListening = listening
        self.waitCTS = False
        self.waitACK = False
        self.notOurCTS = False
        self.name = str(stationName)

    ### destructor
    def __del__(self):
        print("Final counts for Station " + self.name + ":")
        print("Successes     : " + str(self.successes))
        print("Collisions    : " + str(self.collisions))
        print("Left in queue : " + str(self.queue))
        #print("Destroying Station " + self.name)

    def setArrivals(self, arrivalList):
        self.frameArrivals = arrivalList

    def setParams(self,
                    difs,
                    sifs,
                    ack,
                    rts,
                    cts,
                    cw0,
                    cwmax,
                    dataSize):
        self.difsDuration = difs
        self.sifsDuration = sifs
        self.ackDuration = ack
        self.rtsDuration = rts
        self.ctsDuration = cts
        self.contWZero = cw0
        self.contWindow = self.contWZero
        self.contWMax = cwmax
        self.frameSize = dataSize

    def update(self,
            currentSlot):

        nextState = self.status

        # queue any frames that have arrived
        if len(self.frameArrivals) > 0 and currentSlot >= self.frameArrivals[0]:
            print("Station " + self.name + " queued a message! (slot: " + str(currentSlot) + ")")
            self.queue += 1
            self.frameArrivals.pop(0)

        # handle idle state
        if self.status is stationStatus.IDLE and self.queue != 0:
            # need to start trying to send a data frame
            print("Station " + self.name + " changing state to DIFS! (slot: " + str(currentSlot) + ")")
            self.status = stationStatus.DIFS    # don't wait for next slot to begin
            if self.isListening is True and self.channel.getStatus() is channelStatus.RECV:
                nextState = stationStatus.NAV
        elif self.isListening is True and self.status is stationStatus.IDLE and (self.channel.getStatus() is channelStatus.RECV or self.channel.getStatus() is channelStatus.RTSWAIT):
            # channel is busy so go to NAV
            self.status = stationStatus.NAV
        elif self.status is stationStatus.IDLE and self.channel.getStatus() is channelStatus.CTS:
            # another station is using the channel, go to NAV after CTS
            self.notOurCTS = True
            self.status = stationStatus.CTSWAIT

        # DIFS state
        if self.status is stationStatus.DIFS:
            self.currDuration += 1
            if self.useCarrerSense is True and self.channel.getStatus() == channelStatus.CTS:
                self.notOurCTS = True
                nextState = stationStatus.CTSWAIT
            if self.currDuration == self.difsDuration:
                print("Station " + self.name + " in DIFS, next state: BACKOFF! (slot: " + str(currentSlot) + ")")
                nextState = stationStatus.BACKOFF
                self.currDuration = 0
                # get backoff amount
                if self.currBackoff == 0 and self.contWindow > 0:
                    self.backoff = random.randint(0, self.contWindow - 1)
                    print("Station " + self.name + " backoff set: " + str(self.backoff))
                elif self.currBackoff == 0 and self.contWindow == 0:
                    self.backoff = 0
                elif self.currBackoff != 0:
                    print("Station " + self.name + " backoff continued: " + str(self.currBackoff))
            # elif self.currDuration == self.difsDuration and self.useCarrerSense is True:
            #     # next state is actually RTS
            #     self.currDuration = 0
            #     nextState = stationStatus.RTS
            elif self.currDuration < self.difsDuration:
                nextState = stationStatus.DIFS
            if self.isListening is True and self.channel.getStatus() is channelStatus.RECV:
                nextState = stationStatus.NAV
            elif self.isListening is True and self.channel.getStatus() == channelStatus.RTSWAIT:
                nextState = stationStatus.NAV


        # backoff state
        if self.status is stationStatus.BACKOFF and self.backoff > 0:
            self.currBackoff += 1
            if self.useCarrerSense is True and self.channel.getStatus() == channelStatus.CTS:
                self.notOurCTS = True
                nextState = stationStatus.CTSWAIT
            if (self.currBackoff >= self.backoff) and ((self.channel.getStatus() == channelStatus.IDLE) or (self.isListening is False)):
                # we're able to transmit
                print("Station " + self.name + " in BACKOFF, ready to transmit! (slot: " + str(currentSlot) + ")")
                self.channel.acquire(self.name)
                self.currBackoff = 0
                if self.useCarrerSense is False:
                    nextState = stationStatus.TRANSMIT
                else:
                    nextState = stationStatus.RTS

            elif self.isListening is True and (self.channel.getStatus() == channelStatus.RECV or self.channel.getStatus() is channelStatus.SIFS or self.channel.getStatus() is channelStatus.RTSWAIT):
                # someone else has the channel
                nextState = stationStatus.NAV

        elif self.status is stationStatus.BACKOFF and self.backoff == 0:
            # essentially skip this state
            if self.channel.getStatus() == channelStatus.IDLE or self.isListening is False:
                # we're able to transmit
                print("Station " + self.name + " in BACKOFF, ready to transmit! (slot: " + str(currentSlot) + ")")
                self.channel.acquire(self.name)
                self.currBackoff = 0
                if self.useCarrerSense is False:
                    nextState = stationStatus.TRANSMIT
                else:
                    nextState = stationStatus.RTS

        # carrer sensing only: RTS
        if self.status is stationStatus.RTS:
            self.currDuration += 1
            if self.currDuration == self.rtsDuration:
                # wait for CTS
                print("Station " + self.name + " sent RTS! (slot: " + str(currentSlot) + ")")
                self.waitCTS = True
                nextState = stationStatus.SIFS
                self.currDuration = 0

        # transmit
        if self.status is stationStatus.TRANSMIT:
            nextState = stationStatus.TRANSMIT
            self.currDuration += 1
            if self.currDuration == self.frameSize:
                # finished transmitting, enter SIFS
                print("Station " + self.name + " transmit complete! (slot: " + str(currentSlot) + ")")
                self.currDuration = 0
                self.waitACK = True
                nextState = stationStatus.SIFS

        # nav (waiting for channel to clear)
        if self.status is stationStatus.NAV:
            #print("Station " + self.name + " currently in NAV...")
            nextState = stationStatus.NAV
            if self.channel.getStatus() is channelStatus.ACK:
                print("Station " + self.name + " detected ACK while in NAV (slot: " + str(currentSlot) + ")")
                self.currACKDur += 1
                if self.currACKDur == self.ackDuration:
                    # back to DIFS, then resume backoff
                    self.notOurCTS = False
                    self.currACKDur = 0
                    if self.queue > 0:
                        nextState = stationStatus.DIFS
                    else:
                        nextState = stationStatus.IDLE

        # SIFS
        if self.status is stationStatus.SIFS:
            self.currDuration += 1
            if self.currDuration == self.sifsDuration and self.waitCTS is False and self.waitACK is True:
                self.channel.forfeit(self.name)     # release channel
                print("Station " + self.name + " waiting for ACK! (slot: " + str(currentSlot) + ")")
                nextState = stationStatus.ACKWAIT
                self.currDuration = 0
            elif self.currDuration == self.sifsDuration and self.waitCTS is True and self.useCarrerSense is True and self.waitACK is False:
                print("Station " + self.name + " waiting for CTS! (slot: " + str(currentSlot) + ")")
                nextState = stationStatus.CTSWAIT
                self.currDuration = 0
            elif self.currDuration == self.sifsDuration and self.waitCTS is False and self.useCarrerSense is True and self.waitACK is False:
                print("Station " + self.name + " beginning send! (slot: " + str(currentSlot) + ")")
                nextState = stationStatus.TRANSMIT
                self.currDuration = 0

        # waiting for ACK
        if self.status is stationStatus.ACKWAIT:
            self.currDuration += 1
            if self.channel.getStatus() is channelStatus.ACK and self.currDuration == self.ackDuration:
                # success!
                print("Station " + self.name + " successful transmission! (slot: " + str(currentSlot) + ")")
                self.successes += 1
                self.currDuration = 0
                self.queue -= 1                     # since we successfully sent, decrement queue
                self.contWindow = self.contWZero    # reset cw
                self.waitACK = False                # reset waitACK flag
                
                if self.queue > 0:
                    nextState = stationStatus.DIFS  # I think we go back to DIFS?
                else:
                    nextState = stationStatus.IDLE
            elif self.currDuration == self.ackDuration:
                # we've waited but no ACK. Must have been a collision!
                # adjust cw and try again
                print("Station " + self.name + " collision detected! (slot: " + str(currentSlot) + ")")
                self.channel.forfeit(self.name)
                self.currDuration = 0
                self.collisions += 1
                self.contWindow *= 2
                self.waitACK = False                # reset waitACK flag
                if self.contWindow > self.contWMax:
                    self.contWindow = self.contWMax
                nextState = stationStatus.DIFS

        # waiting for CTS
        if self.status is stationStatus.CTSWAIT and self.channel.getStatus() == channelStatus.CTS:
            self.currDuration += 1
            if self.currDuration == self.ctsDuration:
                self.waitCTS = False
                self.currDuration = 0
                if self.notOurCTS is False:
                    print("Station " + self.name + " received CTS! (slot: " + str(currentSlot) + ")")
                    nextState = stationStatus.SIFS
                else:
                    print("Station " + self.name + " detected channel in use! (notOurCTS) Deferring transmission. (slot: " + str(currentSlot) + ")")
                    self.channel.forfeit(self.name) # give up channel
                    nextState = stationStatus.NAV
        elif self.status is stationStatus.CTSWAIT and (self.channel.getStatus() == channelStatus.SIFS or self.channel.getStatus() == channelStatus.RECV):
            # channel is in use
            print("Station " + self.name + " detected channel in use! (CTS passed) Deferring transmission. (slot: " + str(currentSlot) + ")")
            nextState = stationStatus.NAV
            self.notOurCTS = False
            self.waitCTS = False
            self.currDuration = 0
            self.channel.forfeit(self.name) # give up channel
        elif self.status is stationStatus.CTSWAIT and self.channel.getStatus() == channelStatus.IDLE:
            # we ain't gettin a CTS (collision)
            self.currDuration += 1
            if self.currDuration == self.ctsDuration:
                print("Station " + self.name + " timed out waiting for CTS! (slot: " + str(currentSlot) + ")")
                self.channel.forfeit(self.name)
                self.currDuration = 0
                self.waitCTS = False
                self.collisions += 1 # is collision detected here?
                self.contWindow *= 2
                if self.contWindow > self.contWMax:
                    self.contWindow = self.contWMax
                nextState = stationStatus.DIFS # back to DIFS????

        self.status = nextState