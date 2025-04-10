import oslp.protocol as protocol
import gui
import server
from datetime import datetime
import crypto

if __name__ == "__main__":
    # gui.window(p)

    # integer_value = int.from_bytes(data, byteorder='big', signed=False)
    # print(integer_value)
    # x = int(datetime.now().astimezone().utcoffset().total_seconds() / 60)
    # print(x)
    # size = data[1]<<8
    # print(size)
    # crypto.signatureTest()

    # protocol.serializeNotification()
    # protocol.message2()
    # protocol.createConfiguration()

    isTLS = True
    oslpInstance = protocol.protocol("0.0.0.0",12123,isTLS)