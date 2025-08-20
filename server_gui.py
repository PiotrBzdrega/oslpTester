import tkinter as tk
from oslp.types import *
import os
import json
from enum import Enum, auto

class ServerState(Enum):
    none = auto()    # Red-Green-Blue color mode
    start = auto()    # Hexadecimal color mode
    stop = auto()    # Hue-Saturation-Lightness mode

class server_gui:
    def __init__(self,root,start_server,stop_server):
        self.root = root
        self.start_server = start_server
        self.stop_server = stop_server
        self.init_fields()

    def start(self):
        self.start_server()
        self.update_context(ServerState.start)
        
    def stop(self):
        self.stop_server()
        self.update_context(ServerState.stop)

    def read_cache(self):
        # Read JSON data from a file
        if os.path.exists(os.getenv("SERVER_NET_CACHE")):
            try:
                with open(os.getenv("SERVER_NET_CACHE"), 'r') as file:
                    cfg = json.load(file)
                print(cfg)
                self.stored_port = cfg['port'] if 'port' in cfg else "12123"
                self.stored_tls : bool = cfg['tls'] if 'tls' in cfg else True
                self.stored_timeoffset = cfg['timeoffset'] if 'timeoffset' in cfg else "60"
                self.stored_latitude = cfg['latitude'] if 'latitude' in cfg else "52240000"
                self.stored_longitude = cfg['longitude'] if 'longitude' in cfg else "16560000"
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON: {e}")
            except FileNotFoundError:
                print("❌ File not found.")

    def update_cache_tls(self):
        if self.stored_tls != self.tls_var:
            data = {
                "port"          : self.stored_port,
                "tls"           : self.tls_var.get(),
                "timeoffset"    : self.stored_timeoffset,
                "latitude"      : self.stored_latitude,
                "longitude"     : self.stored_longitude
            }
            with open(os.getenv("SERVER_NET_CACHE"), 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            self.stored_tls = self.tls_var.get()

    def update_cache_port(self,new_text):
        if self.stored_port != new_text and self.is_valid_port(new_text):    
            data = {
                "port"  : new_text,
                "tls"   : self.stored_tls,
                "timeoffset"    : self.stored_timeoffset,
                "latitude"      : self.stored_latitude,
                "longitude"     : self.stored_longitude
            }
            with open(os.getenv("SERVER_NET_CACHE"), 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            self.stored_port = new_text

    def update_cache_timeoffset(self,new_text):
        if self.stored_timeoffset != new_text:    
            data = {
                "port"  : self.stored_port,
                "tls"   : self.stored_tls,
                "timeoffset"    : new_text,
                "latitude"      : self.stored_latitude,
                "longitude"     : self.stored_longitude
            }
            with open(os.getenv("SERVER_NET_CACHE"), 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            self.stored_timeoffset = new_text

    def update_cache_latitude(self,new_text):
        if self.stored_latitude != new_text:    
            data = {
                "port"  : self.stored_port,
                "tls"   : self.stored_tls,
                "timeoffset"    : self.stored_timeoffset,
                "latitude"      : new_text,
                "longitude"     : self.stored_longitude
            }
            with open(os.getenv("SERVER_NET_CACHE"), 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            self.stored_latitude = new_text
            
    def update_cache_longitude(self,new_text):
        if self.stored_longitude != new_text:    
            data = {
                "port"  : self.stored_port,
                "tls"   : self.stored_tls,
                "timeoffset"    : self.stored_timeoffset,
                "latitude"      : self.stored_latitude,
                "longitude"     : new_text,
            }
            with open(os.getenv("SERVER_NET_CACHE"), 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            self.stored_longitude = new_text

    def is_valid_port(self,port):
        return 0 <= int(port) <= 65535

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
        
    def validate_timeoffset(self,new_value):
        if not new_value:  # Allow empty field
            return True
        try:
            port = int(new_value)
            if len(new_value)<4:
                self.update_cache_timeoffset(new_value)
                return True
            else:
                return False
        except ValueError:
            return False
        
    def validate_latitude(self,new_value):
        if not new_value:  # Allow empty field
            return True
        try:
            port = int(new_value)
            if len(new_value)<12:
                self.update_cache_latitude(new_value)
                return True
            else:
                return False
        except ValueError:
            return False
        
    def validate_longitude(self,new_value):
        if not new_value:  # Allow empty field
            return True
        try:
            port = int(new_value)
            if len(new_value)<12:
                self.update_cache_longitude(new_value)
                return True
            else:
                return False
        except ValueError:
            return False

    def init_fields(self):
        self.s_frame = tk.LabelFrame(self.root, text="Server")
        self.s_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        # self.s_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
                
        self.startButton = tk.Button(self.s_frame, bg="green", activebackground="lightgreen", text="Start server", command=self.start)
        # self.startButton.pack(pady=10)
        self.startButton.grid(column=0,row=0,columnspan=2)

        self.stopButton = tk.Button(self.s_frame, bg="red", activebackground="lightcoral", text="Stop server", command=self.stop)
        # self.stopButton.grid(column=0,row=1,columnspan=2)
        # self.stopButton.grid_forget()

        self.stored_latitude = "52240000"
        self.stored_longitude ="16560000"
        self.stored_timeoffset = "60"
        self.stored_port ="12123"
        self.stored_tls :bool = True
        self.read_cache()

        # Register validation function for port
        vcmd_port = (self.root.register(self.validate_port), '%P')

        self.port_label = tk.Label(self.s_frame, text="Server port:")
        self.port_label.grid(column=3,row=0)
        self.port_entry = tk.Entry(
            self.s_frame,
            validate="key", # Validate on every keystroke
            validatecommand=vcmd_port,
            width=6,
            font=('Arial', 12))
        self.port_entry.grid(column=4,row=0)
        self.port_entry.insert(-1,self.stored_port)

        self.tls_var = tk.BooleanVar(value=self.stored_tls)
        self.tls_check_box = tk.Checkbutton(self.s_frame, text='TLS',variable=self.tls_var, onvalue=True, offvalue=False, command=self.update_cache_tls)
        self.tls_check_box.grid(column=5,row=0)

        ### Time offset
        self.timeoffset_label = tk.Label(self.s_frame, text="Time offset min.:")
        self.timeoffset_label.grid(column=3,row=1)
        
        # Register validation function for timeout offset
        vcmd_timeoffset = (self.root.register(self.validate_timeoffset), '%P')
        self.timeoffset_entry = tk.Entry(
            self.s_frame,
            validate="key", # Validate on every keystroke
            validatecommand=vcmd_timeoffset,
            width=4,
            font=('Arial', 12))
        self.timeoffset_entry.grid(column=4,row=1)
        self.timeoffset_entry.insert(-1,self.stored_timeoffset)
        
        ### Latitude
        self.latitude_label = tk.Label(self.s_frame, text="Latitude:")
        self.latitude_label.grid(column=3,row=2)
        
        # Register validation function for timeout offset
        vcmd_latitude = (self.root.register(self.validate_latitude), '%P')
        self.latitude_entry = tk.Entry(
            self.s_frame,
            validate="key", # Validate on every keystroke
            validatecommand=vcmd_latitude,
            width=12,
            font=('Arial', 12))       
        self.latitude_entry.grid(column=4,row=2)
        self.latitude_entry.insert(-1,self.stored_latitude)

        ### Longitude
        self.longitude_label = tk.Label(self.s_frame, text="Longitude:")
        self.longitude_label.grid(column=3,row=3)
        
        # Register validation function for timeout offset
        vcmd_longitude = (self.root.register(self.validate_longitude), '%P')
        self.longitude_entry = tk.Entry(
            self.s_frame,
            validate="key", # Validate on every keystroke
            validatecommand=vcmd_longitude,
            width=12,
            font=('Arial', 12))       
        self.longitude_entry.grid(column=4,row=3)
        self.longitude_entry.insert(-1,self.stored_longitude)

    def update_context(self,state : ServerState):
        
        if state != ServerState.none:
            self.startButton.grid_forget()
            self.stopButton.grid_forget()
        
            if state == ServerState.start:
                self.stopButton.grid(column=0,row=0,columnspan=2)
                self.port_label.grid_forget()
                self.port_entry.grid_forget()
                self.tls_check_box.grid_forget()
                
                self.timeoffset_label.grid_forget()
                self.timeoffset_entry.grid_forget()
                
                self.latitude_label.grid_forget()
                self.latitude_entry.grid_forget()
                         
                self.longitude_label.grid_forget()
                self.longitude_entry.grid_forget()       
                
            else:
                self.startButton.grid(column=0,row=0,columnspan=2)
                self.port_label.grid(column=3,row=0)
                self.port_entry.grid(column=4,row=0)
                self.tls_check_box.grid(column=5,row=0)

                self.timeoffset_label.grid(column=3,row=1)
                self.timeoffset_entry.grid(column=4,row=1)

                self.latitude_label.grid(column=3,row=2)
                self.latitude_entry.grid(column=4,row=2)

                self.longitude_label.grid(column=3,row=3)
                self.longitude_entry.grid(column=4,row=3) 
                
