import threading
import os
import server
import client
import oslp.envelope as envelope
import oslp.message as message
import oslp.device as device
from oslp.types import OslpRequestType
import random
import ssl
import crypto
import google.protobuf
import oslp.oslp_pb2 as oslp_pb2 #import the generated protobuf module
from google.protobuf.json_format import MessageToJson, Parse
from queue import Queue
import client_gui
import server_gui
import logging

class protocol:
    def __init__(self,root):
        self.root = root
        self.root.geometry("800x600")
        self.root.title("OSLP Simulator")
        self.queue = Queue()
        self.logger = logging.getLogger('oslp traffic')
        logging.basicConfig(format = '[%(asctime)s] %(message)s', handlers=[logging.FileHandler('traffic_oslp.log'),
            logging.StreamHandler()],  level=logging.DEBUG) #encoding='utf-8', filename='traffic_oslp.log',
        # self.PRIVATE_KEY = os.getenv("PRIVATE_KEY")
        # self.PUBLIC_KEY = os.getenv("PUBLIC_KEY")
        # print(self.PRIVATE_KEY)

        # Create a custom virtual event
        self.root.bind("<<CheckQueue>>", self.handle_queue)

        self.retrieveKey()
        self.dev = device.device(crypto.load_key(os.getenv("PUBLIC_KEY"), public=True))

        self.server = server.server(self.server_handler,self.queue,self.root)
        # self.server = None

        # self.server_thread = threading.Thread(target=self.server.start, name='server_handler')
        self.server_thread : threading.Thread = None

        self.client=client.client(self.prepareRequest,envelope.messageValidator,self.handleResponse,self.dev.setSequenceNumber,self.queue,self.root)

        self.server_states=server_gui.server_gui(self.root,self.start_server,self.stop_server)
        self.client_states=client_gui.client_gui(self.root,self.start_client)


    def handle_queue(self,event):
        
        print("handle_queue")
        msg = self.queue.get()
        msg()

    def start_client(self):
        self.client.start(self.client_states.ip_entry.get(),int(self.client_states.port_entry.get()),self.client_states.tls_var.get())

    def start_server(self):

        if self.server_thread is None or not self.server_thread.is_alive():
            self.server_thread = threading.Thread(target=self.server.start, args=(int(self.server_states.port_entry.get()),self.server_states.tls_var.get()), name='server_handler')    
            self.server_thread.start()
            print("Server started")
        else:
            print("Server is already running, cannot start another instance")

    def stop_server(self):
        
        if self.server_thread is not None:
            if self.server_thread.is_alive():
                # send cancelation token
                self.server.cancel()
            self.server_thread.join()
            self.server_thread = None
            print("Server has been stopped")
        else:
            print("Server is not running, no need to stop")

    def on_button_click(self):
        """Button click handler (runs in main thread)"""
        self.label.config(text=f"Counter from Thread 1: {random.randint(3, 9)}")
        print(f"Button was clicked {random.randint(3, 9)}!")

        # t1.join() #TODO:needed?

    def retrieveKey(self):
        self.privateKey = crypto.load_key(os.getenv("PRIVATE_KEY"), public=False)

    def prepareRequest(self,drop_remaining:bool) -> envelope.envelope:
        request_payload, remaining_msg_parts = message.prepareMessageType(self.client_states,drop_remaining)
        next_sequence = self.dev.getNextSequenceNumber()
        self.logger.debug("[GXF] [%d]\n%s",next_sequence,request_payload)
        request = envelope.envelope(self.dev.getNextSequenceNumberBytes(),self.dev.getDeviceID(),request_payload,privateKey=self.privateKey)
        return (request.encode(),next_sequence,remaining_msg_parts)

    def handleRequest(self,data):
        request = envelope.envelope.decode(data)
        # print("Received request:")
        sequence_number = int.from_bytes(request.sequenceNumber, byteorder='big', signed=False)
        self.logger.debug("[DEV] [%d]\n%s",sequence_number,request.payload)

        self.validateMessage(request)
        response_payload, increment_sequence  = message.checkRequest(request.deviceId,sequence_number,request.payload,self.dev, self.server_states)

        # does this message require sequence increment
        new_success_sequence = self.dev.getNextSequenceNumber() if increment_sequence else self.dev.getSequenceNumber()
        new_success_sequence_bytes = self.dev.getNextSequenceNumberBytes() if increment_sequence else self.dev.getSequenceNumberBytes()           
        # print("Prepared response:")
        self.logger.debug("[GXF] [%d]\n%s",new_success_sequence,response_payload)

        # mirror device id
        response = envelope.envelope(new_success_sequence_bytes,request.deviceId,response_payload,privateKey=self.privateKey)
        return (response.encode(),new_success_sequence)

    def handleResponse(self,data):
        response = envelope.envelope.decode(data)
        self.validateMessage(response)
        sequence_number = int.from_bytes(response.sequenceNumber, byteorder='big', signed=False)
        self.logger.debug("[DEV] [%d]\n%s",sequence_number,response.payload)
        return message.checkResponse(response.deviceId,sequence_number,response.payload,self.dev)

    def validateMessage(self,env:envelope.envelope) -> bool:
        if env.validate(self.dev.publicKey):
            return True
        else:
            raise Exception("Not valid message signature")

    def server_handler(self,client_socket:ssl.SSLSocket,tls:bool):
        buffer = bytearray(4096)  # Create preallocated to store received data
        offset = 0
        with client_socket:
            
            try:
                while True:
                    # Receive the response from the client
                    bytes_received = client_socket.recv_into(memoryview(buffer)[offset:])
                    # print(f"bytes received {bytes_received}",) 
                    if bytes_received == 0:
                        break
                    offset += bytes_received
                    if envelope.messageValidator(buffer[:offset]):
                        raw_response, sequence_number = self.handleRequest(buffer[:offset])
                        offset = 0 
                        client_socket.sendall(raw_response)
                        # set a new sequence number if the data has been delivered
                        self.dev.setSequenceNumber(sequence_number)
                    # print(f"Sent: {message.strip()}"
            except ssl.SSLError as e:
                print(f"SSL error: {e}")
            except Exception as e:
                print(f"Error: {e}")
            finally:
                print("Connection closed")
                if tls:
                    client_socket.unwrap() # Sends TLS close_notify, converts socket to plaintext

                # It disables further sends and receives on the socket, but does not close the socket yet. 
                # This is a TCP-level shutdown, not a TLS-level one.
                # client_socket.shutdown(socket.SHUT_RDWR)

                client_socket.close()
            


        # for n in [0,1,2,3]:
        #     print(n)
        #     time.sleep(1)

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