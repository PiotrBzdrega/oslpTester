import oslp.protocol as protocol
import gui
import test
import tkinter as tk
import os
from signal import signal, SIGPIPE, SIG_IGN

if __name__ == "__main__":

    signal(SIGPIPE,SIG_IGN)

    current_file_path = os.path.abspath(__file__)
    app_root = os.path.dirname(current_file_path)
    os.environ["ROOT_APP"] = app_root
    os.environ["PRIVATE_KEY"] = os.path.join(app_root,"keys/platform_ecdsa_private.pem")
    os.environ["PUBLIC_KEY"] = os.path.join(app_root,"keys/device_ecdsa_public.pem")

    os.environ["CA_ROOT_CERT"] = os.path.join(app_root,"certs/ca.crt") # for client validation
    os.environ["PLATFORM_CERT"] = os.path.join(app_root,"certs/platform.crt") # client/server certificate
    os.environ["PLATFORM_KEY"] = os.path.join(app_root,"certs/platform.key") # client/server certificate private key
    os.environ["NET_CACHE"] = os.path.join(app_root,"net_cache.json") # file to store last used ip

    testing = False
    if testing:
        test.testCheckwindow()
    else:
        root = tk.Tk()
        isTLS = True
        device_server_port = 22125 if isTLS else 12125
        oslpInstance = protocol.protocol("0.0.0.0",12123,"172.20.73.36",device_server_port,isTLS,root)
        
        def on_window_close():
            oslpInstance.stop_server()  # First action
            root.destroy()              # Second action

        root.protocol("WM_DELETE_WINDOW",on_window_close)

        root.mainloop()