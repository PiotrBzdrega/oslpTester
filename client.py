import ssl
import socket
import tkinter as tk
from queue import Queue
from oslp.types import OslpRequestType
import os

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

    def update_label(self,selection):
        # self.selected_label.config(text=f'You chose: {selection}')
        self.selected_label.config(text=f'You chose: {self.oslp_type.get()}')
        print(selection)

    # def on_option_selected(self):
    #     self.selected_label.config(text=f'Selected: {self.oslp_type.get()}')

    def start(self, remote_ip, remote_port):

        print(remote_ip)
        print(remote_port)
        if self.tls and self.context == None:

            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

            # Load client certificate and private key
            context.load_cert_chain(certfile=os.getenv("PLATFORM_CERT"), keyfile=os.getenv("PLATFORM_KEY"))

            # Disable hostname verification
            context.check_hostname = False  

            # Require server certificate for mutual TLS #TODO: not needed already set in PROTOCOL_TLS_CLIENT
            context.verify_mode = ssl.CERT_REQUIRED

            # Load the CA certificate used to verify client certs
            context.load_verify_locations(cafile=os.getenv("CA_ROOT_CERT"))

            # Optional: restrict to TLS 1.3 only
            context.minimum_version = ssl.TLSVersion.TLSv1_3
            context.maximum_version = ssl.TLSVersion.TLSv1_3

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:

            client_socket.settimeout(15)

            # wrap an existing socket with SSLContext
            client_socket = context.wrap_socket(client_socket, server_side=False, server_hostname=remote_ip)
            # client_socket = context.wrap_socket(client_socket, server_side=False)

        try:
            client_socket.connect((remote_ip,remote_port))
            print(f"Successfully connected to {remote_ip} with TLS 1.3")
            print(f"Negotiated cipher: {client_socket.cipher()}")
            print(f"Using protocol: {client_socket.version()}")
            return self.exchange(client_socket)
        except socket.timeout:
            client_socket.close()
            raise Exception(f"Connection to {remote_ip} timed out ")
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
        raw_request, sequence_number = self.prepare_request_handler()
        try:
            socket.sendall(raw_request)
            # set a new sequence number if the data has been delivered
            self.set_sequence_number(sequence_number)
            while True:
                # Receive the response from the server
                bytes_received = socket.recv_into(memoryview(buffer)[offset:])
                # print(f"{bytes_received} bytes received from Server") 
                if bytes_received == 0:
                    break
                offset += bytes_received
                if self.msg_validator(buffer[:offset]):
                    self.response_handler(buffer[:offset])
                    break


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





