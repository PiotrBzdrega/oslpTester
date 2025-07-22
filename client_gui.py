from datetime import datetime,timezone
import tkinter as tk
from oslp.types import *
import os
import json
import ipaddress

class client_gui:
    def __init__(self,root,client_request):
        self.root = root
        self.client_request = client_request
        self.init_fields()

    @staticmethod
    def list_directories(directory:str):
        schedules_path = os.path.join(os.getenv("ROOT_APP"),directory)
        onlydir = [dir for dir in os.listdir(schedules_path) if os.path.isdir(os.path.join(schedules_path, dir))]
        # print(schedules_path)
        # print(onlydir)
        onlydir.sort()
        return onlydir
    
    @staticmethod
    def list_dir_json_files(parent_dir:str,schedule_dir):
        schedules_path = os.path.join(os.getenv("ROOT_APP"),parent_dir,schedule_dir)
        # print(schedules_path)
        onlyfile = [
            os.path.join(schedules_path, filename) 
            for filename in os.listdir(schedules_path) 
            if os.path.isfile(os.path.join(schedules_path, filename) ) and os.path.splitext(os.path.join(schedules_path, filename))[1].lower() == ".json" # second element holds the file extension
            ]
        # print(onlyfile)
        onlyfile.sort()
        return onlyfile

    def update_option_context(self,selected_value):

        # self.time_label.pack_forget()
        # self.time.pack_forget()
        # self.day_night_radio.pack_forget()
        # self.night_day_radio.pack_forget()

        # SetTransition
        self.time_label.grid_forget()
        self.time.grid_forget()
        self.day_night_radio.grid_forget()
        self.night_day_radio.grid_forget()

        # SetSchedule
        self.schedule_label.grid_forget()
        self.om.grid_forget()

        # SetLight
        self.setlight_label.grid_forget()
        self.om_setlight.grid_forget()

        # SetConfiguration
        self.setconfiguration_label.grid_forget()
        self.om_setconfiguration.grid_forget()

        # SetNotificationMask
        self.event_label.grid_forget()
        self.event_mask.grid_forget()

        # ResumeSchedule
        self.resume_label.grid_forget()
        self.resume_idx.grid_forget()
        self.immediate_check_box.grid_forget()


        match self.oslp_type.get():
            case OslpRequestType.setTransitionRequest:
                # self.time_label.pack(pady=10)
                # self.time.pack()
                # self.day_night_radio.pack()
                # self.night_day_radio.pack()
                self.time_label.grid(column=0,row=2)
                self.time.grid(column=0,row=3)
                self.day_night_radio.grid(column=1,row=3)
                self.night_day_radio.grid(column=1,row=4)

            case OslpRequestType.setLightRequest:
                #Update OptionMenu elements
                setlight_menu = self.om_setlight["menu"]
                setlight_menu.delete(0, "end")
                self.om_setlight_options = client_gui.list_dir_json_files("SetLight","")
                for string in self.om_setlight_options:
                    setlight_menu.add_command(label=string, 
                             command=lambda value=string: self.setlight_dir.set(value))
                self.setlight_label.grid(column=0,row=2)  
                self.om_setlight.grid(column=0,row=3)
            case OslpRequestType.setConfigurationRequest:
                #Update OptionMenu elements
                setconfiguration_menu = self.om_setconfiguration["menu"]
                setconfiguration_menu.delete(0, "end")
                self.om_setconfiguration_options = client_gui.list_dir_json_files("SetConfiguration","")
                for string in self.om_setconfiguration_options:
                    setconfiguration_menu.add_command(label=string, 
                             command=lambda value=string: self.setconfiguration_dir.set(value))
                self.setconfiguration_label.grid(column=0,row=2)  
                self.om_setconfiguration.grid(column=0,row=3) 
            # case OslpRequestType.setConfigurationRequest:
            #     raise NotImplementedError("doit")  
            case OslpRequestType.resumeScheduleRequest:
                self.resume_label.grid(column=0,row=2)
                self.resume_idx.grid(column=0,row=3)
                self.immediate_check_box.grid(column=1,row=3)

            case OslpRequestType.setEventNotificationsRequest:
                self.event_label.grid(column=0,row=2)
                self.event_mask.grid(column=0,row=3)
 
            case OslpRequestType.setScheduleRequest:
                #Update OptionMenu elements
                menu = self.om["menu"]
                menu.delete(0, "end")
                self.om_options = client_gui.list_directories("SetSchedule")
                for string in self.om_options:
                    menu.add_command(label=string, 
                             command=lambda value=string: self.schedule_dir.set(value))
                self.schedule_label.grid(column=0,row=2)  
                self.om.grid(column=0,row=3)     

            # case OslpRequestType.startSelfTestRequest:       
            # case OslpRequestType.stopSelfTestRequest:
            # case OslpRequestType.getStatusRequest:
            # case OslpRequestType.getConfigurationRequest:
            # case OslpRequestType.setRebootRequest:
            # case OslpRequestType.getFirmwareVersionResponse 
            # do nix

    def read_cache(self):
        # Read JSON data from a file
        if os.path.exists(os.getenv("CLIENT_NET_CACHE")):
            try:
                with open(os.getenv("CLIENT_NET_CACHE"), 'r') as file:
                    cfg = json.load(file)
                print(cfg)
                self.stored_ip = cfg['ip'] if 'ip' in cfg else "0.0.0.0"
                self.stored_port = cfg['port'] if 'port' in cfg else "22125"
                self.stored_tls : bool = cfg['tls'] if 'tls' in cfg else True
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON: {e}")
            except FileNotFoundError:
                print("❌ File not found.")

    def update_cache_tls(self):
        if self.stored_tls != self.tls_var:
            data = {
                "ip"    : self.stored_ip,
                "port"  : self.stored_port,
                "tls"   : self.tls_var.get()
            }
            with open(os.getenv("CLIENT_NET_CACHE"), 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            self.stored_tls = self.tls_var.get()

    def is_valid_port(self,port):
        return 0 <= int(port) <= 65535
        
    def update_cache_port(self,new_text):
        if self.stored_port != new_text and self.is_valid_port(new_text):    
            data = {
                "ip"    : self.stored_ip,
                "port"  : new_text,
                "tls"   : self.stored_tls
            }
            with open(os.getenv("CLIENT_NET_CACHE"), 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            self.stored_port = new_text

    def validate_port(self,new_value):
        if not new_value:  # Allow empty field
            return True
        try:
            port = int(new_value)
            if len(new_value)<6 and self.is_valid_port(port):
                self.update_cache_port(new_value)
                return True
            else:
                return False
        except ValueError:
            return False

    def is_valid_ip(self,ip):
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

    def update_cache_ip(self,new_text):
        if self.stored_ip != new_text and self.is_valid_ip(new_text):    
            data = {
                "ip"    : new_text,
                "port"  : self.stored_port,
                "tls"   : self.stored_tls
            }
            with open(os.getenv("CLIENT_NET_CACHE"), 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            self.stored_ip = new_text

    def validate_ip(self,new_text):
        # Check if the new text is a valid partial IP
        parts = new_text.split('.')
        if len(parts) > 4:
            return False  # Too many parts

        for part in parts:
            if not part.isdigit() and part != "":  # Allow empty during typing
                return False
            if part and (int(part) < 0 or int(part) > 255):
                return False
        
        if self.is_valid_ip(new_text):
            self.update_cache_ip(new_text)
        return True

    def init_fields(self):
        self.c_frame = tk.LabelFrame(self.root, text="Client")
        self.c_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        # self.c_frame.grid()
        # self.c_label = tk.Label(self.c_frame, text="Counter from Thread 1: 0")
        # self.c_label.pack(pady=10)
        
        # self.selected_label1 = tk.Label(self.c_frame, text="adam")
        # self.selected_label1.pack(pady=10)

        self.oslp_type = tk.StringVar(self.c_frame)
        self.oslp_type.set(OslpRequestType.startSelfTestRequest)

        # self.droplist = tk.OptionMenu(self.c_frame,self.oslp_type, *OSLP_type, command=self.update_label)
        self.droplist = tk.OptionMenu(self.c_frame,self.oslp_type, *OslpRequestType,command=self.update_option_context)
        # self.droplist.config(indicatoron=False,background="orange")  # Hide the indicator
        # self.droplist.pack(pady=20)
        self.droplist.grid(column=0,row=0)

        self.send_request_button = tk.Button(self.c_frame, bg="yellow", activebackground="lightyellow", text="Send request", command=self.client_request)
        self.send_request_button.grid(column=1,row=0)

        """ CACHE NETWORK """
        self.stored_ip ="0.0.0.0"
        self.stored_port ="22125"
        self.stored_tls :bool = True
        self.read_cache()

        # def format_ip(event=None):
        #     current_text = self.ip_entry.get()
        #     if current_text.count('.') == 3 and len(current_text.split('.')) == 4:
        #         # If it's a complete IP, process it (e.g., store or print)
        #         print("Valid IP:", current_text)
        #     else:
        #         # Optional: Auto-insert '.' after 3 digits
        #         if len(current_text.replace('.', '')) % 3 == 0 and current_text[-1] != '.':
        #             self.ip_entry.insert(tk.END, '.')

        # Register validation function for port
        vcmd_port = (self.root.register(self.validate_port), '%P')

        self.port_label = tk.Label(self.c_frame, text="Device port:")
        self.port_label.grid(column=2,row=2)
        self.port_entry = tk.Entry(
            self.c_frame,
            validate="key", # Validate on every keystroke
            validatecommand=vcmd_port,
            width=6,
            font=('Arial', 12))
        self.port_entry.grid(column=2,row=3)
        self.port_entry.insert(-1,self.stored_port)

        # Register validation function for ip
        vcmd_ip = (self.root.register(self.validate_ip), '%P')

        self.ip_label = tk.Label(self.c_frame, text="Device IPv4:")
        self.ip_label.grid(column=2,row=0)
        self.ip_entry = tk.Entry(
            self.c_frame,
            validate="key", # Validate on every keystroke
            validatecommand=vcmd_ip,
            width=15,
            font=('Arial', 12))
        self.ip_entry.grid(column=2,row=1)
        self.ip_entry.insert(-1,self.stored_ip)

        self.tls_var = tk.BooleanVar(value=self.stored_tls)
        self.tls_check_box = tk.Checkbutton(self.c_frame, text='TLS',variable=self.tls_var, onvalue=True, offvalue=False, command=self.update_cache_tls)
        self.tls_check_box.grid(column=2,row=4)

        """ CACHE NETWORK """

        """ SET TRANSITION """
        def validate_transition(new_text):
           return (new_text.isdigit() and len(new_text) <= 14) or new_text==""

        # Register the validation function
        validate_cmd = self.root.register(validate_transition)

        self.time_label = tk.Label(self.c_frame, text="transitionTime")
        # self.time_label.pack(pady=10)

        self.time = tk.Entry(self.c_frame,validate="key", validatecommand=(validate_cmd, '%P'), width=15)
        utc_now = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        self.time.insert(-1,utc_now)
        # self.time.pack()

        self.trans_radvar = tk.StringVar(self.c_frame,value=OslpTransitionType.night_day)

        self.day_night_radio = tk.Radiobutton(self.c_frame,text=OslpTransitionType.day_night, variable=self.trans_radvar , value=OslpTransitionType.day_night)
        # self.day_night_radio.pack()

        self.night_day_radio = tk.Radiobutton(self.c_frame,text=OslpTransitionType.night_day, variable=self.trans_radvar , value=OslpTransitionType.night_day)
        # self.night_day_radio.pack()
        """ SET TRANSITION """    

        """ SET SCHEDULE """
        self.schedule_label = tk.Label(self.c_frame, text="Directory with schedule file/s")
        self.om_options = client_gui.list_directories("SetSchedule")
        self.schedule_dir = tk.StringVar(self.c_frame)
        self.schedule_dir.set(self.om_options[0])
        self.om = tk.OptionMenu(self.c_frame, self.schedule_dir, *self.om_options) #,command=self.update_option_context # does not work

        """ SET SCHEDULE """

        """ SET LIGHT """
        self.setlight_label = tk.Label(self.c_frame, text="Directory with SetLight templates")
        self.om_setlight_options = client_gui.list_dir_json_files("SetLight","")
        self.setlight_dir = tk.StringVar(self.c_frame)
        self.setlight_dir.set(self.om_setlight_options[0])
        self.om_setlight = tk.OptionMenu(self.c_frame, self.setlight_dir, *self.om_setlight_options) 

        """ SET LIGHT """

        """ SET EVENT NOTIFICATIONS """
        self.event_label = tk.Label(self.c_frame, text="Event Mask")

        def validate_mask_func(new_value):
            if new_value == "":  # Allow empty field (for backspace/delete)
                return True
            try:
                value = int(new_value)
                return 0 <= value <= 255
            except ValueError:
                return False

        # Register the validation function
        validate_mask = self.root.register(validate_mask_func)

        self.event_mask = tk.Entry(self.c_frame,validate="key", validatecommand=(validate_mask, '%P'), width=5)
        self.event_mask.insert(-1,255)

        """ SET EVENT NOTIFICATIONS """

        """ RESUME SCHEDULE """
        self.resume_label = tk.Label(self.c_frame, text="Index (empty for all configured switches)")

        def validate_idx_func(new_value):
            if new_value == "":  # Allow empty field (for backspace/delete)
                return True
            try:
                value = int(new_value)
                return 1 <= value <= 9
            except ValueError:
                return False

        # Register the validation function
        validate_idx = self.root.register(validate_idx_func)

        self.resume_idx = tk.Entry(self.c_frame,validate="key", validatecommand=(validate_idx, '%P'), width=1)

        self.immediate_var = tk.BooleanVar()
        self.immediate_check_box = tk.Checkbutton(self.c_frame, text='Immediate',variable=self.immediate_var, onvalue=True, offvalue=False)

        """ RESUME SCHEDULE """

        """ SET CONFIGURATION """
        self.setconfiguration_label = tk.Label(self.c_frame, text="Directory with SetConfiguration templates")
        self.om_setconfiguration_options = client_gui.list_dir_json_files("SetConfiguration","")
        self.setconfiguration_dir = tk.StringVar(self.c_frame)
        self.setconfiguration_dir.set(self.om_setconfiguration_options[0])
        self.om_setconfiguration = tk.OptionMenu(self.c_frame, self.setconfiguration_dir, *self.om_setconfiguration_options) 

        """ SET CONFIGURATION """
