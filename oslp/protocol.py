import threading
import time
import os
import server
import oslp.envelope as envelope
import oslp.message as message
import oslp.device as device
import ssl
import crypto
import google.protobuf
import oslp.oslp_pb2 as oslp_pb2 #import the generated protobuf module
from google.protobuf.json_format import MessageToJson, Parse

class protocol:
    def __init__(self,ip: str, port: int, tls: bool):
        self.retrieveKey()
        self.dev = device.device(crypto.load_key(crypto.PUBLIC_KEY, public=True))
        self.server = server.server(ip,port,tls)
        self.server.add_handler(handler=self.server_handler)
        self.t1 = threading.Thread(target=self.server.start, name='server_handler')

        self.t1.start()

        # t1.join() #TODO:needed?

    def retrieveKey(self):
        self.privateKey = crypto.load_key(crypto.PRIVATE_KEY, public=False)

    def handleIncommingData(self,data):
        request = envelope.envelope.decode(data)
        if request.validate(self.dev.publicKey):
            response_payload = message.handleMessage(request.deviceId,int.from_bytes(request.sequenceNumber, byteorder='big', signed=False),request.payload,self.dev)
        else:
            raise Exception("Not valid message signature")

        response = envelope.envelope(self.dev.getSequenceNumberBytes(),self.dev.deviceUid,response_payload,privateKey=self.privateKey)
        return response.encode()
        

    def server_handler(self,client_socket=None):

        buffer = bytearray(4096)  # Create preallocated to store received data
        offset = 0
        with client_socket:
            
            try:
                while True:
                    # Receive the response from the client
                    bytes_received = client_socket.recv_into(memoryview(buffer)[offset:])
                    if bytes_received == 0:
                        break
                    offset += bytes_received
                    print(bytes_received)
                    if envelope.messageValidator(buffer[:offset]):
                        raw_response = self.handleIncommingData(buffer[:offset])
                        offset = 0 
                        client_socket.sendall(raw_response)

                    # 
                    # print(f"Sent: {message.strip()}"
            except Exception as e:
                print(f"Error: {e}")
            finally:
                print("Close the connection1") 
                client_socket.close()
            


        for n in [0,1,2,3]:
            print(n)
            time.sleep(1)
     


def protobuf_ver():
    print("protobuf v"+google.protobuf.__version__)

def message2():
    msg = oslp_pb2.Message()
    request = msg.registerDeviceRequest
    request.deviceIdentification = "adam"
    request.ipAddress = bytes([1,2,3,4])
    request.deviceType = oslp_pb2.DeviceType.SSLD;
    request.hasSchedule = False
    request.randomDevice = 12345
    # json_string = MessageToJson(msg)
    # print("JSON representation:")
    # print(json_string)
    # Parse(json_string, msg)
    # if msg.HasField("registerDeviceRequest"):
        # print("request" , msg.registerDeviceRequest)
    # if msg.HasField("registerDeviceResponse"):
        # print("response", msg.registerDeviceResponse)

    # Serialize the message to bytes
    # serialized_bytes = msg.SerializeToString()

    # Print the serialized bytes
    # print("Serialized bytes:", serialized_bytes)

    # new_message = oslp_pb2.Message()
    # new_message.ParseFromString(serialized_bytes)



    # print(new_message)

    device_id = bytes([1,2,3,4,5,6,7,8,9,10,11,12])
    sequence_number = bytes([2,0])
    

    privat = crypto.load_key(crypto.PRIVATE_KEY, public=False)
    env1 = envelope.envelope(sequence_number,device_id,msg,privat)


    encoded = env1.encode()
    string = " ".join(str(byte) for byte in encoded)
    # print(string)

    env2 = envelope.envelope.decode(encoded)

    
    # print("signature created "," ".join(str(byte) for byte in request.securityKey))
    # print("signature received"," ".join(str(byte) for byte in receive.securityKey))

    # print("dataToSign created "," ".join(str(byte) for byte in request.dataToSign()))
    # print("dataToSign received"," ".join(str(byte) for byte in receive.dataToSign()))

    print("decoded",env2.payload)
    public = privat.public_key()

    # public = crypto.load_key(crypto.PUBLIC_KEY, public=True)

    if env2.validate(public):
        print("validated")
    else:
        print("not validated")

def serializeNotification():
    notifs = oslp_pb2.EventNotificationRequest()

    notif = oslp_pb2.EventNotification()
    notif.event = oslp_pb2.Event.SECURITY_EVENTS_INVALID_CERTIFICATE
    notif.index = b'\x01'
    notif.description = "Is"
    notif.timestamp = "20250226094500"
    notifs.notifications.append(notif)

    print(notifs)
    binary_data = notifs.SerializeToString()

    # Write to file
    with open("notifications2.pb", "wb") as f:
        f.write(binary_data)
    print("Message saved to notification.pb")    

def createConfiguration():
    request =  oslp_pb2.SetConfigurationRequest()
    request.lightType = oslp_pb2.LightType.RELAY
    request.deviceFixIpValue = b"\300\250\000n"
    request.netMask = b"\377\377\377\000"
    request.gateWay = b"\300\250\000\001"
    request.isDhcpEnabled = False
    # request.isTlsEnabled = False
    # request.oslpBindPortNumber = 1234
    # request.commonNameString = "TLS Test"
    request.communicationTimeout = 15
    request.communicationNumberOfRetries = 2
    request.communicationPauseTimeBetweenConnectionTrials = 120
    request.ospgIpAddress = b"\300\250d*"
    request.osgpPortNumber = 12125
    request.isTestButtonEnabled = False
    request.isAutomaticSummerTimingEnabled = True
    request.astroGateSunRiseOffset = -15
    request.astroGateSunSetOffset = 15
    request.switchingDelay.extend([100, 200, 300, 400])
    request.relayRefreshing = True
    request.summerTimeDetails = "0360100"
    request.winterTimeDetails = "1060200"

    relay_config = request.relayConfiguration.addressMap.add()
    relay_config.index = b"\001"
    relay_config.address = b"\000"
    relay_config.relayType = oslp_pb2.TARIFF

    relay_config = request.relayConfiguration.addressMap.add()
    relay_config.index = b"\002"
    relay_config.address = b"\001"
    relay_config.relayType = oslp_pb2.LIGHT

    relay_config = request.relayConfiguration.addressMap.add()
    relay_config.index = b"\003"
    relay_config.address = b"\002"
    relay_config.relayType = oslp_pb2.LIGHT

    relay_config = request.relayConfiguration.addressMap.add()
    relay_config.index = b"\004"
    relay_config.address = b"\003"
    relay_config.relayType = oslp_pb2.LIGHT

    json_string = MessageToJson(request)
    print("JSON representation:")
    print(json_string)

    # Write to file
    with open("cfg.json", "w") as f:
        f.write(json_string)

    # Serialize to bytes    
    serialized_data = request.SerializeToString()

    # Deserialize from bytes
    new_response = oslp_pb2.SetConfigurationRequest()
    new_response.ParseFromString(serialized_data)

    print(new_response)



def message1():
    msg = oslp_pb2.Message()
    registerDeviceResponse = oslp_pb2.RegisterDeviceResponse()
    registerDeviceResponse.status = oslp_pb2.Status.OK
    registerDeviceResponse.currentTime = "20250226094500"
    registerDeviceResponse.randomDevice = 123456
    registerDeviceResponse.randomPlatform = 654321

    # Create and set LocationInfo
    location = oslp_pb2.LocationInfo()
    location.timeOffset = 120  # UTC+2 hours
    location.latitude = int(37.7749 * 1000000)  # Convert float to int
    location.longitude = int(-122.4194 * 1000000)  # Convert float to int

    registerDeviceResponse.locationInfo.CopyFrom(location)

    json_string = MessageToJson(registerDeviceResponse)
    print("JSON representation:")
    print(json_string)

    # Serialize to bytes    
    serialized_data = registerDeviceResponse.SerializeToString()

    # Deserialize from bytes
    new_response = oslp_pb2.RegisterDeviceResponse()
    new_response.ParseFromString(serialized_data)

    print(new_response)


    # # Example JSON string
    # json_text = """
    # {
    #     "schedules": [
    #         {
    #           "weekday": "ALL",
    #           "actionTime": "SUNRISE",
    #           "window": {
    #             "minutesBefore": 15,
    #             "minutesAfter": 15
    #           },
    #           "value": [
    #             {
    #               "index": "AQ==",
    #               "on": false
    #             }
    #           ],
    #           "triggerType": "LIGHT_TRIGGER"
    #         }
    #     ],
    #     "scheduleType": "LIGHT"
    # }
    # """

    # Create an empty Person message
    person = oslp_pb2.SetScheduleRequest()

    # Read the binary data from the file
    with open("schedule1.json", "r") as f:
        json_text = f.read()
        # Parse JSON into the Protobuf message
        Parse(json_text, person)

    # Now person is populated
    print("Parsed Protobuf message:")
    print(person)

    # Serialize to string (in binary format)
    binary_data = person.SerializeToString()

    # Write to file
    with open("schedule1.pb", "wb") as f:
        f.write(binary_data)

    print("Message saved to schedule1.pb")