import oslp.oslp_pb2 as oslp_pb2 #import the generated protobuf module
import oslp.envelope as envelope
import oslp.device as device


# OslpChannelHandlerServer.java channelRead0
registerDeviceRequestData = bytes([48, 69, 2, 33, 0, 246, 220, 203, 199, 139, 42, 174, 152, 247, 55, 239, 164, 106, 106, 240, 208, 88, 213, 130, 194, 224, 35, 175, 27, 134, 199, 197, 243, 149, 174, 236, 131, 2, 32, 110, 170, 13, 81, 199, 7, 124, 14, 68, 42, 202, 82, 71, 177, 81, 233, 101, 121, 44, 173, 165, 90, 182, 249, 112, 202, 233, 58, 88, 12, 218, 199, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 46, 24, 0, 4, 30, 21, 122, 253, 47, 73, 152, 99, 246, 10, 0, 34, 10, 32, 10, 8, 50, 51, 52, 48, 48, 52, 51, 54, 18, 12, 49, 55, 50, 46, 50, 48, 46, 55, 51, 46, 51, 51, 24, 1, 32, 0, 40, 155, 139, 3])

def handleMessage(msg):
    return processMessage(msg)

def processMessage(msg):
    if msg.HasField("registerDeviceRequest"):
        return handleRegisterDeviceRequest(msg)
    elif msg.HasField("confirmRegisterDeviceRequest"):
        return handleConfirmRegisterDeviceRequest(msg)
    elif msg.HasField("setEventNotificationsRequest"):
        return handleSetEventNotificationsRequest(msg)
    else:
        raise Exception("Not correct message type")     
        


def handleRegisterDeviceRequest(msg):
    raise NotImplementedError

def handleConfirmRegisterDeviceRequest(msg):
    raise NotImplementedError

def handleSetEventNotificationsRequest(msg):
    raise NotImplementedError