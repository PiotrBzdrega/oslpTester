import random

class device:
    def __init__(self):
        self.deviceUid = None
        self.deviceIdentification = None
        self.deviceType = None
        self.sequenceNumber = None
        self.randomPlatform = None
        self.randomDevice = None
    
    def updateRegisterData(self,device_uid, device_type, random_device):
        self.deviceUid = device_uid
        self.deviceType = device_type
        self.sequenceNumber = None
        self.randomDevice = random_device
        self.randomPlatform = random.ranrange(0, 2^16-1) # randomPlatform has 16bit

    def setSequenceNumber(self,sequence_number):
        self.sequenceNumber = sequence_number
