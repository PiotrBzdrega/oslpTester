import oslp.oslp_pb2 as oslp_pb2 #import the generated protobuf module
import oslp.device as device
from datetime import datetime,timezone
from oslp.types import *
import client_gui
from google.protobuf.json_format import Parse

# OslpChannelHandlerServer.java channelRead0

# integer_value.to_bytes(length=length, byteorder='big', signed=False)

def prepareMessageType(client_states:client_gui.client_gui):
    print(f"function: {prepareMessageType.__name__}({type})")
    msg = oslp_pb2.Message()    
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
            msg.setEventNotificationsRequest.NotificationMask = 255
        case OslpRequestType.setScheduleRequest:
            schedule = oslp_pb2.SetScheduleRequest()
            dir=client_states.schedule_dir.get()
            partial_schedule = client_states.list_dir_json_files("SetSchedule",dir)
            # print(f"partial_schedule: {partial_schedule}")
            #TODO: missing handling for multiple files
            with open(partial_schedule[0], "r") as f:
                json_text = f.read()
                # Parse JSON into the Protobuf message
                Parse(json_text, schedule)
                msg.setScheduleRequest.CopyFrom(schedule)

            # raise NotImplementedError("doit")
        case OslpRequestType.getConfigurationRequest:
            msg.getConfigurationRequest.CopyFrom(oslp_pb2.GetConfigurationRequest())
        case OslpRequestType.setConfigurationRequest:
            configuration = oslp_pb2.SetConfigurationRequest()

            with open(client_states.configuration_dir.get(), "r") as f:
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

        case _:
            raise Exception(f"Not correct message type {prepareMessageType.__name__}")
    print("Prepared message type")
    print(msg)
    return msg

def checkResponse(device_uid,sequence_number,payload,dev):
    if ( 
        payload.HasField("startSelfTestResponse") or
        payload.HasField("stopSelfTestResponse") or
        payload.HasField("stopSelfTestResponse") or
        payload.HasField("setLightResponse") or
        payload.HasField("getStatusResponse") or
        payload.HasField("resumeScheduleResponse") or
        payload.HasField("setEventNotificationsResponse") or
        payload.HasField("setScheduleResponse") or
        payload.HasField("setRebootResponse") or
        payload.HasField("setTransitionResponse") or
        payload.HasField("getConfigurationResponse") or
        payload.HasField("setConfigurationRequest")
    ):
        if dev.checkSequenceNumber(sequence_number):
            dev.setSequenceNumber(sequence_number)
            print("Received message")
            print(payload)
    else:
        raise Exception(f"Not correct message type {checkResponse.__name__}")     

def checkRequest(device_uid,sequence_number,payload,dev):
    if payload.HasField("registerDeviceRequest"):
        return (handleRegisterDeviceRequest(device_uid,sequence_number,payload.registerDeviceRequest,dev),False)
    elif payload.HasField("confirmRegisterDeviceRequest"):
        return (handleConfirmRegisterDeviceRequest(device_uid,sequence_number,payload.confirmRegisterDeviceRequest,dev),False)
    elif payload.HasField("eventNotificationRequest"):
        # Only sequece number for EventNotificationsRequest should be incremented
        return (handleEventNotificationsRequest(device_uid,sequence_number,payload.eventNotificationRequest,dev),True)
    else:
        raise Exception(f"Not correct message type {checkRequest.__name__}") 

def handleRegisterDeviceRequest(device_uid,sequence_number,registerDeviceRequest,dev):

    dev.updateRegisterData(device_uid,registerDeviceRequest.deviceType,registerDeviceRequest.randomDevice)
    dev.setSequenceNumber(sequence_number)

    msg = oslp_pb2.Message()
    response = msg.registerDeviceResponse
    response.status = oslp_pb2.Status.OK
    response.currentTime = datetime.now(tz=None).strftime("%Y%m%d%H%M%S")
    response.randomDevice = dev.getRandomDevice()
    response.randomPlatform = dev.getRandomPlatform()
    location = response.locationInfo
    location.timeOffset = int(datetime.now().astimezone().utcoffset().total_seconds() / 60) # in minutes
    location.latitude  = 52240000
    location.longitude = 16560000

    return msg

def handleConfirmRegisterDeviceRequest(device_uid,sequence_number,confirmRegisterDeviceRequest,dev):    
    msg = oslp_pb2.Message()
    response = msg.confirmRegisterDeviceResponse

    if (dev.checkDeviceAndPlatformRandom(confirmRegisterDeviceRequest.randomDevice,confirmRegisterDeviceRequest.randomPlatform) and
        dev.checkSequenceNumber(sequence_number)):
            dev.setSequenceNumber(sequence_number)
            response.status = oslp_pb2.Status.OK
            response.randomDevice = dev.getRandomDevice()
            response.randomPlatform = dev.getRandomPlatform()
            response.sequenceWindow = device.SEQUENCE_WINDOW
            return msg
    else:
        response.status = oslp_pb2.Status.REJECTED

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