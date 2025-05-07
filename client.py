import ssl
import socket
import tkinter as tk
from queue import Queue
from oslp.types import OslpRequestType
from datetime import datetime,timezone

ca_root_cert  = "/certs/ca.crt"         # for client validation
platform_cert = "/certs/platform.crt"   # client/server certificate
platform_key  = "/certs/platform.key"   # client/server certificate private key

class client:
    def __init__(self, prepare_request_handler, msg_validator, response_handler, set_sequence_number, server_ip="0.0.0.0", port=12125, tls=True, queue: Queue =None,root:tk.Tk=None):
        self.server_ip = server_ip
        self.port = port
        self.tls = tls
        self.queue = queue
        self.root = root
        self.context:ssl.SSLContext = None
        self.prepare_request_handler = prepare_request_handler
        self.msg_validator = msg_validator
        self.response_handler = response_handler
        self.set_sequence_number = set_sequence_number
        self.gui_update(self.gui_init)

    def gui_update(self,func):
        self.queue.put(func)
        # self.root.event_generate("<<CheckQueue>>",data="adam")
        self.root.event_generate("<<CheckQueue>>")

    def gui_init(self):

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

        self.send_request_button = tk.Button(self.c_frame, text="Send request", command=self.start)
        self.send_request_button.pack(pady=10)

        """ SET TRANSITION """
        self.time_label = tk.Label(self.c_frame, text="transitionTime")
        self.time_label.pack(pady=10)
        self.time = tk.Entry(self.c_frame, width=15)
        utc_now = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        self.time.insert(-1,utc_now)
        self.time.pack(pady=10)

        """ SET TRANSITION """
        

    def update_label(self,selection):
        # self.selected_label.config(text=f'You chose: {selection}')
        self.selected_label.config(text=f'You chose: {self.oslp_type.get()}')
        print(selection)

    # def on_option_selected(self):
    #     self.selected_label.config(text=f'Selected: {self.oslp_type.get()}')

    def start(self):

        if self.tls and self.context == None:

            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

            # Load client certificate and private key
            context.load_cert_chain(certfile=platform_cert, keyfile=platform_key)

            # Disable hostname verification
            context.check_hostname = False  

            # Require server certificate for mutual TLS #TODO: not needed already set in PROTOCOL_TLS_CLIENT
            context.verify_mode = ssl.CERT_REQUIRED

            # Load the CA certificate used to verify client certs
            context.load_verify_locations(cafile=ca_root_cert)

            # Optional: restrict to TLS 1.3 only
            context.minimum_version = ssl.TLSVersion.TLSv1_3
            context.maximum_version = ssl.TLSVersion.TLSv1_3

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:

            client_socket.settimeout(15)

            # wrap an existing socket with SSLContext
            client_socket = context.wrap_socket(client_socket, server_side=False, server_hostname=self.server_ip)
            # client_socket = context.wrap_socket(client_socket, server_side=False)

        try:
            client_socket.connect((self.server_ip,self.port))
            print(f"Successfully connected to {self.server_ip} with TLS 1.3")
            print(f"Negotiated cipher: {client_socket.cipher()}")
            print(f"Using protocol: {client_socket.version()}")
            return self.exchange(client_socket)
        except socket.timeout:
            client_socket.close()
            raise Exception(f"Connection to {self.server_ip} timed out ")
        except Exception as e:
            client_socket.close()
            raise Exception(f"Failed to establish secure connection: {str(e)}")      

                # while not self.ct.is_canceled():
                #     client_socket, client_address = server_socket.accept()
                #     print(f"Connection from {client_address}")
                #     self.handler(client_socket)
                #     print("Server waits for the next request")
                # print("Server stopped")
            
    def exchange(self,socket:ssl.SSLSocket):
        buffer = bytearray(4096)  # Create preallocated to store received data
        offset = 0
        raw_request, sequence_number = self.prepare_request_handler(self.oslp_type.get())
        try:
            socket.sendall(raw_request)
            # set a new sequence number if the data has been delivered
            self.set_sequence_number(sequence_number)
            while True:
                # Receive the response from the server
                bytes_received = socket.recv_into(memoryview(buffer)[offset:])
                print(f"{bytes_received} bytes received from Server") 
                if bytes_received == 0:
                    break
                offset += bytes_received
                if self.msg_validator(buffer[:offset]):
                    self.response_handler(buffer[:offset])


        except ssl.SSLError as e:
            print(f"SSL error: {e}")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            print("Close the connection")            
            if self.tls:
                socket.unwrap() # Sends TLS close_notify, converts socket to plaintext
            # It disables further sends and receives on the socket, but does not close the socket yet. 
            # This is a TCP-level shutdown, not a TLS-level one.
            # client_socket.shutdown(socket.SHUT_RDWR)
            socket.close()





