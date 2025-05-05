import oslp.device as device
import crypto

def testCheckwindow():
    dev = device.device(crypto.load_key(crypto.PUBLIC_KEY, public=True))

    dev.setSequenceNumber(1)

    assert dev.checkSequenceNumber(0)       ==True
    assert dev.checkSequenceNumber(1)       ==True
    assert dev.checkSequenceNumber(2)       ==True
    assert dev.checkSequenceNumber(3)       ==True
    assert dev.checkSequenceNumber(4)       ==True
    assert dev.checkSequenceNumber(5)       ==True
    assert dev.checkSequenceNumber(6)       ==True
    assert dev.checkSequenceNumber(7)       ==True
    assert dev.checkSequenceNumber(8)       ==True

    assert dev.checkSequenceNumber(9)       ==False
    assert dev.checkSequenceNumber(10)      ==False

    assert dev.checkSequenceNumber(65535)   ==True
    assert dev.checkSequenceNumber(65534)   ==True
    assert dev.checkSequenceNumber(65533)   ==True
    assert dev.checkSequenceNumber(65532)   ==True

    assert dev.checkSequenceNumber(65531)   ==False
    assert dev.checkSequenceNumber(65530)   ==False

    dev.setSequenceNumber(65530)

    assert dev.checkSequenceNumber(65531)   ==True
    assert dev.checkSequenceNumber(65532)   ==True
    assert dev.checkSequenceNumber(65533)   ==True
    assert dev.checkSequenceNumber(65534)   ==True
    assert dev.checkSequenceNumber(65535)   ==True
    assert dev.checkSequenceNumber(0)       ==True
    assert dev.checkSequenceNumber(1)       ==True
    assert dev.checkSequenceNumber(2)       ==False
    assert dev.checkSequenceNumber(3)       ==False

    dev.setSequenceNumber(65535)

    assert dev.checkSequenceNumber(65528)   ==False
    assert dev.checkSequenceNumber(65529)   ==False

    assert dev.checkSequenceNumber(65530)   ==True
    assert dev.checkSequenceNumber(65531)   ==True
    assert dev.checkSequenceNumber(65532)   ==True
    assert dev.checkSequenceNumber(65533)   ==True
    assert dev.checkSequenceNumber(65534)   ==True
    assert dev.checkSequenceNumber(65535)   ==True
    assert dev.checkSequenceNumber(0)       ==True
    assert dev.checkSequenceNumber(1)       ==True
    assert dev.checkSequenceNumber(2)       ==True
    assert dev.checkSequenceNumber(3)       ==True
    assert dev.checkSequenceNumber(4)       ==True
    assert dev.checkSequenceNumber(5)       ==True
    assert dev.checkSequenceNumber(6)       ==True

    assert dev.checkSequenceNumber(7)       ==False
    assert dev.checkSequenceNumber(8)       ==False

# def checkWindow(v1,v2,maxNumber,win):
#     diff = abs(v1-v2)
#     if diff > win:
#         if diff <= (maxNumber-win):
#             return False
#     return True

# def testCheckwindow():
#     if checkWindow(0,65535,65535,6):
#         print("OK")
#     else:
#         print("not OK")

#   print(crypto.create_hash("124"))

    # oslp.protobuf_ver()