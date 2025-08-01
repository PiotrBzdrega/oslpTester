import oslp.protocol as protocol
import test
import tkinter as tk
import os
from signal import signal, SIGPIPE, SIG_IGN
# import ssh

if __name__ == "__main__":

    # ssh.connect()
    # exit(1)

    signal(SIGPIPE,SIG_IGN)

    current_file_path = os.path.abspath(__file__)
    app_root = os.path.dirname(current_file_path)
    os.environ["ROOT_APP"] = app_root
    os.environ["PRIVATE_KEY"] = os.path.join(app_root,"keys/platform_ecdsa_private.pem")
    os.environ["PUBLIC_KEY"] = os.path.join(app_root,"keys/device_ecdsa_public.pem")

    os.environ["CA_ROOT_CERT"] = os.path.join(app_root,"certs/ca.crt") # for client validation
    os.environ["PLATFORM_CERT"] = os.path.join(app_root,"certs/platform.crt") # client/server certificate
    os.environ["PLATFORM_KEY"] = os.path.join(app_root,"certs/platform.key") # client/server certificate private key
    os.environ["CLIENT_NET_CACHE"] = os.path.join(app_root,"client_net_cache.json") # file to store last used ip and port
    os.environ["SERVER_NET_CACHE"] = os.path.join(app_root,"server_net_cache.json") # file to store last used port
    os.environ["OSLP_CACHE"] = os.path.join(app_root,"oslp_cache.json") # file to store oslp registration details

    testing = False
    if testing:
        test.testCheckwindow()
    else:
        root = tk.Tk()
        oslpInstance = protocol.protocol(root)
        
        def on_window_close():
            oslpInstance.stop_server()  # First action
            root.destroy()              # Second action

        root.protocol("WM_DELETE_WINDOW",on_window_close)

        root.mainloop()