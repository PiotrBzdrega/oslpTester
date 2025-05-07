import oslp.oslp_pb2 as oslp_pb2 #import the generated protobuf module
import oslp.device as device
from datetime import datetime,timezone
from oslp.types import OslpRequestType

# OslpChannelHandlerServer.java channelRead0

# integer_value.to_bytes(length=length, byteorder='big', signed=False)

def prepareMessageType(type:OslpRequestType):
    print(f"function: {prepareMessageType.__name__}({type})")
    msg = oslp_pb2.Message()    
    match type:
        case OslpRequestType.startSelfTestRequest:
            msg.startSelfTestRequest.CopyFrom(oslp_pb2.StartSelfTestRequest())
        case OslpRequestType.stopSelfTestRequest:
            msg.stopSelfTestRequest.CopyFrom(oslp_pb2.StopSelfTestRequest())
        case OslpRequestType.setLightRequest:
            msg.setLightRequest.CopyFrom(oslp_pb2.SetLightRequest())
            value1 = oslp_pb2.LightValue()
            value1.on = True
            # value1.index = b'\x01'

            # value2 = oslp_pb2.LightValue()
            # value2.on = False
            # value2.index = b'\x02'
            msg.setLightRequest.values.append(value1)
        case OslpRequestType.getStatusRequest:
            msg.getStatusRequest.CopyFrom(oslp_pb2.GetStatusRequest())
        case OslpRequestType.resumeScheduleRequest:
            msg.resumeScheduleRequest.CopyFrom(oslp_pb2.ResumeScheduleRequest())
            msg.resumeScheduleRequest.immediate = True
            # msg.resumeScheduleRequest.index = 1/2/3/4
        case OslpRequestType.setEventNotificationsRequest:
            msg.setEventNotificationsRequest.CopyFrom(oslp_pb2.SetEventNotificationsRequest())
            msg.setEventNotificationsRequest.NotificationMask = 255
        case OslpRequestType.setScheduleRequest:
            raise NotImplementedError("doit")
        case OslpRequestType.setRebootRequest:
            msg.setRebootRequest.CopyFrom(oslp_pb2.SetRebootRequest())
        case OslpRequestType.setTransitionRequest:
            msg.setTransitionRequest.CopyFrom(oslp_pb2.SetTransitionRequest())
            msg.setTransitionRequest.transitionType = oslp_pb2.TransitionType.NIGHT_DAY # oslp_pb2.TransitionType.DAY_NIGHT
            msg.setTransitionRequest.time = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        case _:
            raise Exception("Not correct message type")
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
        payload.HasField("setTransitionResponse")
    ):
        if dev.checkSequenceNumber(sequence_number):
            dev.setSequenceNumber(sequence_number)
            print("Received message")
            print(payload)
    else:
        raise Exception("Not correct message type")     

def checkRequest(device_uid,sequence_number,payload,dev):
    if payload.HasField("registerDeviceRequest"):
        return (handleRegisterDeviceRequest(device_uid,sequence_number,payload.registerDeviceRequest,dev),False)
    elif payload.HasField("confirmRegisterDeviceRequest"):
        return (handleConfirmRegisterDeviceRequest(device_uid,sequence_number,payload.confirmRegisterDeviceRequest,dev),False)
    elif payload.HasField("eventNotificationRequest"):
        # Only sequece number for EventNotificationsRequest should be incremented
        return (handleEventNotificationsRequest(device_uid,sequence_number,payload.eventNotificationRequest,dev),True)
    else:
        raise Exception("Not correct message type") 

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