import google.protobuf
import crypto
import oslp.oslp_pb2 as oslp_pb2 #import the generated protobuf module
import oslp.device as device

SECURITY_KEY_SIZE = 128
SEQUENCE_NUMBER_SIZE = 2
DEVICE_ID_SIZE = 12
LEN_INDICATOR_SIZE = 2
ENVELOPE_FIXED_SIZE = SECURITY_KEY_SIZE + SEQUENCE_NUMBER_SIZE + DEVICE_ID_SIZE + LEN_INDICATOR_SIZE

class envelope:
    def __init__(self, sequenceNumber, deviceId, payload, privateKey=None, securityKey=None):
        self.sequenceNumber = sequenceNumber
        self.deviceId = deviceId
        self.payload = payload
        self.privateKey = privateKey
        if securityKey==None:
            self.setSecurityKey()
        else:
            self.securityKey = securityKey

    def dataToSign(self) -> bytes:
        serialize_payload = self.payload.SerializeToString()
        payload_len = len(serialize_payload)
        dataToSign = self.sequenceNumber + self.deviceId + payload_len.to_bytes(length=2, byteorder='big', signed=False) + serialize_payload
        return dataToSign

    def setSecurityKey(self):
        signature = crypto.sign(self.privateKey,self.dataToSign())
        sign_with_padding = signature + bytes(128-len(signature)) # 128 is signature max length
        # print("setSecurityKey","sign_with_padding"," ".join(str(byte) for byte in sign_with_padding))
        self.securityKey = sign_with_padding
    
    def validate(self,publicKey) -> bool:
        signature_size = 2+self.securityKey[1] # [0] - something, [1] - length
        signature = self.securityKey[:signature_size]
        # print("validate","signature1"," ".join(str(byte) for byte in signature))
        result = crypto.verify(publicKey,self.dataToSign(),signature)
        return result

    def encode(self) -> bytes:
        return self.securityKey + self.dataToSign()

    @classmethod
    def decodeSecurityKey(cls,data):
        return cls.retrieveField(data,SECURITY_KEY_SIZE)

    @classmethod
    def decodeSequnceNumber(cls,data):
        return cls.retrieveField(data,SEQUENCE_NUMBER_SIZE)

    @classmethod
    def decodeDeviceId(cls,data):
        return cls.retrieveField(data,DEVICE_ID_SIZE)

    @classmethod
    def decodepayload(cls,data):
        len = cls.retrieveField(data,LEN_INDICATOR_SIZE)

        # print(len(data))
        proto = oslp_pb2.Message()
        proto.ParseFromString(data)
        # print message
        # print(proto)
        return proto

    @classmethod
    def retrieveField(cls,data,size):
        field = data[:size]
        del data[:size]
        return field

    @classmethod
    def decode(cls, data):
        if not messageValidator(data):
            raise Exception("messageValidator")
        raw_data = bytearray(data)
        # print(len(raw_data))
        security_key = cls.decodeSecurityKey(raw_data)
        # print(len(raw_data))
        sequence_number = cls.decodeSequnceNumber(raw_data)
        # intseq = int.from_bytes(sequence_number, byteorder='big', signed=False)
        # print("sequence_number received"," ".join(str(byte) for byte in sequence_number))
        # print("intseq",intseq)
        # print(len(raw_data))
        device_id = cls.decodeDeviceId(raw_data)
        # print(len(raw_data))
        payload = cls.decodepayload(raw_data)
        return cls(sequence_number,device_id,payload,securityKey=security_key)

def messageValidator(data):
    data_len = len(data)
    # print("enelope size",data_len)
    data_len-=ENVELOPE_FIXED_SIZE
    # envelope must be longer than fixed size part 
    if data_len <= 0:
        return False
    
    msg_len = (data[ENVELOPE_FIXED_SIZE-LEN_INDICATOR_SIZE] <<8) + data[ENVELOPE_FIXED_SIZE-LEN_INDICATOR_SIZE+1]

    if data_len == msg_len:
        return True

    return False
