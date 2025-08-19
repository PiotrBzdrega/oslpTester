import oslp.oslp_pb2 as oslp_pb2 #import the generated protobuf module
import oslp.device as device
from datetime import datetime,timezone
from oslp.types import *
import client_gui
import server_gui
from google.protobuf.json_format import Parse
from google.protobuf import descriptor
from collections import deque

def prepareMessageType(client_states:client_gui.client_gui, drop_remaining : bool = True):
    if not hasattr(prepareMessageType, "msg_remainder"):
        prepareMessageType.msg_remainder = deque([])  # Initialize
        print("initialization msg_remainder")
    msg = oslp_pb2.Message()
    
    if drop_remaining and len(prepareMessageType.msg_remainder)>0:
        # delete all messages if it is not desired to continue sending parial msg
        print(f"drop all remaining messages:{len(prepareMessageType.msg_remainder)}")
        prepareMessageType.msg_remainder.clear()

    if len(prepareMessageType.msg_remainder)>0:
        # print(f"{prepareMessageType.msg_remainder}")
        print(f"remaining msg parts:{len(prepareMessageType.msg_remainder)}")
        # append partial schedule to message
        # pop element added as first
        pop_schedule=prepareMessageType.msg_remainder.popleft()
        msg.setScheduleRequest.CopyFrom(pop_schedule)
        
    # no more partial messages    
    else:
        match client_states.oslp_type.get():
            case OslpRequestType.startSelfTestRequest:
                msg.startSelfTestRequest.CopyFrom(oslp_pb2.StartSelfTestRequest())
            case OslpRequestType.stopSelfTestRequest:
                msg.stopSelfTestRequest.CopyFrom(oslp_pb2.StopSelfTestRequest())
            case OslpRequestType.setLightRequest:
                set_light_proto = oslp_pb2.SetLightRequest()

                with open(client_states.setlight_dir.get(), "r") as f:
                    json_set_light = f.read()
                    # Parse JSON into the Protobuf message
                    Parse(json_set_light, set_light_proto)
                    msg.setLightRequest.CopyFrom(set_light_proto)

                # value1 = oslp_pb2.LightValue()
                # value1.on = True
                # value1.index = b'\x01'

                # value2 = oslp_pb2.LightValue()
                # value2.on = False
                # value2.index = b'\x02'
                # msg.setLightRequest.values.append(value1)
            case OslpRequestType.getStatusRequest:
                msg.getStatusRequest.CopyFrom(oslp_pb2.GetStatusRequest())
            case OslpRequestType.resumeScheduleRequest:
                msg.resumeScheduleRequest.CopyFrom(oslp_pb2.ResumeScheduleRequest())
                msg.resumeScheduleRequest.immediate = client_states.immediate_var.get()

                if client_states.resume_idx.get() != "":
                    index:int = int(client_states.resume_idx.get())
                    index_bytes = index.to_bytes(length=1, byteorder='big', signed=False)
                    print(index_bytes)
                    msg.resumeScheduleRequest.index = index_bytes

            case OslpRequestType.setEventNotificationsRequest:
                msg.setEventNotificationsRequest.CopyFrom(oslp_pb2.SetEventNotificationsRequest())
                msg.setEventNotificationsRequest.NotificationMask = int(client_states.event_mask.get())
            case OslpRequestType.setScheduleRequest:
                dir=client_states.schedule_dir.get()
                partial_schedule = client_states.list_dir_json_files("SetSchedule",dir)
                print(f"partial_schedule: {partial_schedule}")
                #TODO: missing handling for multiple files
                for idx, item in enumerate(partial_schedule):
                    schedule = oslp_pb2.SetScheduleRequest()
                    with open(item, "r") as f:
                        json_text = f.read()
                        # Parse JSON into the Protobuf message
                        Parse(json_text, schedule)
                        if idx==0:
                            print(f"prepare schedule: {item} for send")
                            # store in slot to send only first message
                            msg.setScheduleRequest.CopyFrom(schedule)
                        else:
                            # rest messages store for later
                            print(f"store schedule: {item} for later send")
                            prepareMessageType.msg_remainder.append(schedule)
                            
                    # print(f"All elements \n:{prepareMessageType.msg_remainder}")

                # raise NotImplementedError("doit")
            case OslpRequestType.getConfigurationRequest:
                msg.getConfigurationRequest.CopyFrom(oslp_pb2.GetConfigurationRequest())
            case OslpRequestType.setConfigurationRequest:
                configuration = oslp_pb2.SetConfigurationRequest()

                with open(client_states.setconfiguration_dir.get(), "r") as f:
                    json_set_configuration = f.read()
                    # Parse JSON into the Protobuf message
                    Parse(json_set_configuration, configuration)
                    msg.setConfigurationRequest.CopyFrom(configuration)

            case OslpRequestType.setRebootRequest:
                msg.setRebootRequest.CopyFrom(oslp_pb2.SetRebootRequest())
            case OslpRequestType.setTransitionRequest:
                msg.setTransitionRequest.CopyFrom(oslp_pb2.SetTransitionRequest())

                if client_states.trans_radvar.get() == OslpTransitionType.night_day:
                    msg.setTransitionRequest.transitionType = oslp_pb2.TransitionType.NIGHT_DAY
                else:
                    msg.setTransitionRequest.transitionType = oslp_pb2.TransitionType.DAY_NIGHT

                # Specify time if field not empty
                if client_states.time.get():
                    msg.setTransitionRequest.time = client_states.time.get()
                # .. otherwise send without time -> device will take now
                # msg.setTransitionRequest.time = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
            
            case OslpRequestType.getFirmwareVersionRequest:
                msg.getFirmwareVersionRequest.CopyFrom(oslp_pb2.GetFirmwareVersionRequest())

            case _:
                raise Exception(f"Not correct message type {prepareMessageType.__name__}")
    # print("Prepared message type")
    return (msg, len(prepareMessageType.msg_remainder) > 0) # pass information if there are still remaining parts of message

def checkResponse(device_uid,sequence_number,payload ,dev:device.device):
    status=None
    if payload.HasField("startSelfTestResponse"):
        status =  payload.startSelfTestResponse.status
    elif payload.HasField("stopSelfTestResponse"):
        status =  payload.stopSelfTestResponse.status
    elif payload.HasField("setLightResponse"):
        status =  payload.setLightResponse.status
    elif payload.HasField("getStatusResponse"):
        status =  payload.getStatusResponse.status
    elif payload.HasField("resumeScheduleResponse"):
        status =  payload.resumeScheduleResponse.status
    elif payload.HasField("setEventNotificationsResponse"):
        status =  payload.setEventNotificationsResponse.status
    elif payload.HasField("setScheduleResponse"):
        status =  payload.setScheduleResponse.status
    elif payload.HasField("setRebootResponse"):
        status =  payload.setRebootResponse.status
    elif payload.HasField("setTransitionResponse"):
        status =  payload.setTransitionResponse.status
    elif payload.HasField("getConfigurationResponse"):
        status =  payload.getConfigurationResponse.status
    elif payload.HasField("setConfigurationResponse"):
        status =  payload.setConfigurationResponse.status
    elif payload.HasField("getFirmwareVersionResponse"):
        # this msg does not have Status field
        status = oslp_pb2.Status.OK
    else:
        raise Exception(f"Not correct message type {checkResponse.__name__}")     
    
    if status is not None and dev.checkSequenceNumber(sequence_number):
        dev.setSequenceNumber(sequence_number)
        # print(f"Status value: {status}")
        # return false if msg did not received OK
        return status == oslp_pb2.Status.OK
        
    return False


def checkRequest(device_uid,sequence_number,payload,dev, server_states:server_gui.server_gui):
    if payload.HasField("registerDeviceRequest"):
        return (handleRegisterDeviceRequest(device_uid,sequence_number,payload.registerDeviceRequest,dev,server_states),False)
    elif payload.HasField("confirmRegisterDeviceRequest"):
        return (handleConfirmRegisterDeviceRequest(device_uid,sequence_number,payload.confirmRegisterDeviceRequest,dev),False)
    elif payload.HasField("eventNotificationRequest"):
        # Only sequece number for EventNotificationsRequest should be incremented
        # update: seems none message sequence number should be incremented 
        return (handleEventNotificationsRequest(device_uid,sequence_number,payload.eventNotificationRequest,dev),False)
    else:
        raise Exception(f"Not correct message type {checkRequest.__name__}") 

def handleRegisterDeviceRequest(device_uid,sequence_number,registerDeviceRequest,dev, server_states:server_gui.server_gui):

    dev.updateRegisterData(device_uid,registerDeviceRequest.deviceType,registerDeviceRequest.randomDevice)
    dev.setSequenceNumber(sequence_number)

    msg = oslp_pb2.Message()
    response = msg.registerDeviceResponse
    response.status = oslp_pb2.Status.OK
    response.currentTime = datetime.now(tz=None).strftime("%Y%m%d%H%M%S")
    response.randomDevice = dev.getRandomDevice()
    response.randomPlatform = dev.getRandomPlatform()
    location = response.locationInfo 
    location.timeOffset = int(server_states.timeoffset_entry.get()) #int(datetime.now().astimezone().utcoffset().total_seconds() / 60) # in minutes
    location.latitude  = int(server_states.latitude_entry.get()) #52240000
    location.longitude = int(server_states.longitude_entry.get()) #16560000

    return msg

def handleConfirmRegisterDeviceRequest(device_uid,sequence_number,confirmRegisterDeviceRequest,dev):    
    msg = oslp_pb2.Message()
    response = msg.confirmRegisterDeviceResponse

    if (dev.checkDeviceAndPlatformRandom(confirmRegisterDeviceRequest.randomDevice,confirmRegisterDeviceRequest.randomPlatform) and
        dev.checkSequenceNumber(sequence_number)):
        dev.setSequenceNumber(sequence_number)
        response.status = oslp_pb2.Status.OK
    else:
        response.status = oslp_pb2.Status.REJECTED

    response.randomDevice = dev.getRandomDevice()
    response.randomPlatform = dev.getRandomPlatform()
    response.sequenceWindow = device.SEQUENCE_WINDOW

    return msg

def handleEventNotificationsRequest(device_uid,sequence_number,eventNotificationRequest,dev):
    msg = oslp_pb2.Message()
    response = msg.eventNotificationResponse

    if dev.checkSequenceNumber(sequence_number):
            dev.setSequenceNumber(sequence_number)
            response.status = oslp_pb2.Status.OK
    else:
        response.status = oslp_pb2.Status.REJECTED

    return msg