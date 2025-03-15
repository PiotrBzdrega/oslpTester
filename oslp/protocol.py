import threading
import time
import os
import server
import oslp.envelope as envelope
import oslp.message as message
import oslp.device as device
import crypto
import google.protobuf
import oslp.oslp_pb2 as oslp_pb2 #import the generated protobuf module
from google.protobuf.json_format import MessageToJson, Parse

class protocol:
    def __init__(self):
        self.retrieveKeys()
        self.device = device.device()
        self.server = server.server()
        self.server.add_handler(handler=self.server_handler)
        self.t1 = threading.Thread(target=self.server.start, name='server_handler')

        self.t1.start()

        # t1.join() #TODO:needed

    def retrieveKeys(self):
        self.public  = crypto.load_key(crypto.TEST_PUBLIC_KEY, public=True)
        self.private = crypto.load_key(crypto.TEST_PRIVATE_KEY, public=False)

    def handleIncommingData(self,envelope):
        request = envelope.envelope.decode(envelope)
        if request.validate(self.publicKey):
            response_payload = message.handleMessage(request.payload,self.device)
        else:
            raise Exception("Not valid message signature")

        response = envelope.envelope(self.device.sequenceNumber,self.device.deviceUid,response_payload,privateKey=self.private)
        

    def server_handler(self,client_socket=None):

        buffer = bytearray(4096)  # Create preallocated to store received data
        offset =0
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
                        request = envelope.envelope.decode(buffer[:offset])
                        if request.validate(self.public):
                            print(f"Client response: {buffer[:offset]}")


                    
                    # client_socket.sendall(message.encode())
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
    json_string = MessageToJson(msg)
    print("JSON representation:")
    print(json_string)
    Parse(json_string, msg)
    if msg.HasField("registerDeviceRequest"):
        print("request" , msg.registerDeviceRequest)
    if msg.HasField("registerDeviceResponse"):
        print("response", msg.registerDeviceResponse)

    # Serialize the message to bytes
    serialized_bytes = msg.SerializeToString()

    # Print the serialized bytes
    print("Serialized bytes:", serialized_bytes)

    new_message = oslp_pb2.Message()
    new_message.ParseFromString(serialized_bytes)



    print(new_message)




def message():
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