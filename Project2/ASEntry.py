from enum import Enum

class linkType(Enum):
    P2P = 'p2p' # peer to peer
    P2C = 'p2c' # provider to customer


# holds values for each AS link entry
class ASEntry():

    ### ctor
    def __init__(self,
            as1,
            as2,
            type):
        self.as1 = as1
        self.as2 = as2
        if type == -1:
            self.type = linkType.P2C
        else:
            self.type = linkType.P2P
    
    # def __del__(self):
        # do nothing lol

    def __str__(self):
        return "AS1: " + str(self.as1) + " AS2: " + str(self.as2) + " Type: " + self.type.value