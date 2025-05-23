import oslp.protocol as protocol
import gui
import test
import tkinter as tk
from signal import signal, SIGPIPE, SIG_IGN

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

    signal(SIGPIPE,SIG_IGN)

    testing = False
    
    if testing:
        test.testCheckwindow()
    else:
        root = tk.Tk()
        isTLS = True
        oslpInstance = protocol.protocol("0.0.0.0",12123,"172.20.73.33",12125,isTLS,root)

        
        def on_window_close():
            oslpInstance.stop_server()  # First action
            root.destroy()              # Second action

        root.protocol("WM_DELETE_WINDOW",on_window_close)

        root.mainloop()
        # tk._test()

