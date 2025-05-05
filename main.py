import oslp.protocol as protocol
import gui
import test
import tkinter as tk

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

    testing = False
    
    if testing:
        test.testCheckwindow()
    else:
        root = tk.Tk()
        isTLS = True
        oslpInstance = protocol.protocol("0.0.0.0",12123,"172.20.73.33",12125,isTLS,root)
        root.mainloop()
        # tk._test()

