import oslp.oslp_pb2 as oslp_pb2 #import the generated protobuf module
import oslp.device as device
from datetime import datetime
from oslp.types import OslpRequestType

# OslpChannelHandlerServer.java channelRead0

# integer_value.to_bytes(length=length, byteorder='big', signed=False)

def prepareMessageType(type:OslpRequestType):
    print(f"function: {prepareMessageType.__name__}({type})")
    msg = oslp_pb2.Message()
    match type:
        case OslpRequestType.startSelfTestRequest:
            print("start_selftest_request")
        case OslpRequestType.stopSelfTestRequest:
            print("stop_selftest_request")
        case OslpRequestType.setLightRequest:
            print("set_light_request")
        case OslpRequestType.getStatusRequest:
            msg.getStatusRequest
        case OslpRequestType.resumeScheduleRequest:
            print("resume_schedule_request")
        case OslpRequestType.setEventNotificationsRequest:
            print("set_event_notifications_request")
        case OslpRequestType.setScheduleRequest:
            print("set_schedule_request")
        case OslpRequestType.setRebootRequest:
            print("set_reboot_request")
        case OslpRequestType.setTransitionRequest:
            print("set_transition_request")
        case _:
            raise Exception("Not correct message type")
    return msg

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