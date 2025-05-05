import random
import json
import os

MAX_SEQUENCE_NUMBER = pow(2,16) - 1
SEQUENCE_WINDOW = 6
CFG_FILE = 'cache.json'

class device:
    def __init__(self,publicKey):
        self.deviceUid = None
        self.deviceIdentification = None
        self.deviceType = None
        self.sequenceNumber = None
        self.randomPlatform = None
        self.randomDevice = None
        self.publicKey = publicKey
        self.readConfig()
    
    def readConfig(self):
        # Read JSON data from a file
        if os.path.exists(CFG_FILE):
            try:
                with open(CFG_FILE, 'r') as file:
                    cfg = json.load(file)
                print(cfg)
                self.randomDevice   = cfg['randomDevice']
                self.randomPlatform = cfg['randomPlatform']
                self.sequenceNumber = cfg['sequenceNumber']
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON: {e}")
            except FileNotFoundError:
                print("❌ File not found.")

    def writeConfig(self):
        data = {
            "deviceUid"             : int.from_bytes(self.deviceUid, byteorder='big', signed=False),
            # "deviceIdentification"  : int.from_bytes(self.deviceIdentification, byteorder='big', signed=False),
            "randomDevice"          : self.randomDevice,
            "randomPlatform"        : self.randomPlatform,
            "sequenceNumber"        : 0
        }
        with open(CFG_FILE, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def updateSequenceNumberInConfig(self,sequenceNumber : int):
        # Read JSON data from a file
        if os.path.exists(CFG_FILE):
            try:
                with open(CFG_FILE, 'r') as file:
                    cfg = json.load(file)
                cfg['sequenceNumber'] = sequenceNumber

                with open(CFG_FILE, 'w', encoding='utf-8') as file:
                    json.dump(cfg, file, ensure_ascii=False, indent=4)
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON: {e}")
            except FileNotFoundError:
                print("❌ File not found.")
    
    def updateRegisterData(self,device_uid, device_type, random_device):
        self.deviceUid = device_uid
        self.deviceType = device_type
        self.sequenceNumber = None
        self.randomDevice = random_device
        self.randomPlatform = random.randrange(0, pow(2,16) - 1) # randomPlatform has 16bit
        self.writeConfig()

    # Make sure that returns format that needed, here bytes
    def getDeviceID(self):
        return self.deviceUid

    def setSequenceNumber(self,sequence_number : int):
        print(f"New sequence number {sequence_number}")
        self.sequenceNumber = sequence_number
        self.updateSequenceNumberInConfig(sequence_number)

    def getSequenceNumber(self):
        return self.sequenceNumber
    
    def getNextSequenceNumber(self) -> int:
        next = self.sequenceNumber + 1
        return 0 if next > MAX_SEQUENCE_NUMBER else next
    
    def getSequenceNumberBytes(self) -> bytes:
        return self.sequenceNumber.to_bytes(length=2, byteorder='big', signed=False)
    
    def getNextSequenceNumberBytes(self) -> bytes:
        return self.getNextSequenceNumber().to_bytes(length=2, byteorder='big', signed=False)    

    def getRandomDevice(self):
        return self.randomDevice

    def getRandomPlatform(self):
        return self.randomPlatform
    
    def checkSequenceNumber(self,sequence_number):
        expect_sequence_number = self.sequenceNumber + 1
        if expect_sequence_number > MAX_SEQUENCE_NUMBER:
            expect_sequence_number = 0
        
        diff = abs(expect_sequence_number-sequence_number)
        if diff > SEQUENCE_WINDOW:
            if diff <= (MAX_SEQUENCE_NUMBER - SEQUENCE_WINDOW):
                print(f'Wrong sequence number. Should be {expect_sequence_number} +/-{SEQUENCE_WINDOW}, received {sequence_number}')
                return False 

        return True          
                   

    def checkDeviceAndPlatformRandom(self,device_random,platform_random):
        if self.randomDevice != device_random :
            print(f'Wrong device random. Should be {self.randomDevice} received {device_random}')
            return False
        if self.randomPlatform != platform_random :
            print(f'Wrong platform random. Should be {self.randomPlatform} received {platform_random}')
            return False
        return True
