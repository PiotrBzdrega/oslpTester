from datetime import datetime,timezone
import tkinter as tk
from oslp.types import OslpRequestType

class client_gui:
    def __init__(self,root,client_request):
        self.root = root
        self.client_request = client_request
        self.init_fields()

    def init_fields(self):
        self.c_frame = tk.LabelFrame(self.root, text="Client")
        self.c_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # self.c_label = tk.Label(self.c_frame, text="Counter from Thread 1: 0")
        # self.c_label.pack(pady=10)
        
        self.selected_label1 = tk.Label(self.c_frame, text="adam")
        self.selected_label1.pack(pady=10)

        self.oslp_type = tk.StringVar(self.c_frame)
        self.oslp_type.set(OslpRequestType.getStatusRequest)

        # self.droplist = tk.OptionMenu(self.c_frame,self.oslp_type, *OSLP_type, command=self.update_label)
        self.droplist = tk.OptionMenu(self.c_frame,self.oslp_type, *OslpRequestType)
        # self.droplist.config(indicatoron=False,background="orange")  # Hide the indicator
        self.droplist.pack(pady=20)

        self.send_request_button = tk.Button(self.c_frame, text="Send request", command=self.client_request)
        self.send_request_button.pack(pady=10)

        """ SET TRANSITION """
        self.time_label = tk.Label(self.c_frame, text="transitionTime")
        self.time_label.pack(pady=10)
        self.time = tk.Entry(self.c_frame, width=15)
        utc_now = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        self.time.insert(-1,utc_now)
        self.time.pack(pady=10)

        """ SET TRANSITION """    
