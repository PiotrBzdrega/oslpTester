
def checkWindow(v1,v2,maxNumber,win):
    diff = abs(v1-v2)
    if diff > win:
        if diff <= (maxNumber-win):
            return False
    return True

def testCheckwindow():
    if checkWindow(0,65535,65535,6):
        print("OK")
    else:
        print("not OK")

#   print(crypto.create_hash("124"))

    # oslp.protobuf_ver()