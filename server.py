import ssl
import socket
import tkinter as tk
from tkinter import ttk
from queue import Queue
import cancellation
import select
import os

class server:
    def __init__(self, handler, host="0.0.0.0", port=12123, tls=True, queue: Queue =None,root:tk.Tk=None):
        self.ct = cancellation.CancellationToken()
        self.host = host
        self.port = port
        self.tls = tls
        self.queue = queue
        self.root = root
        self.handler = handler
        # Create wakeup socket pair
        self.wakeup_r = -1
        self.wakeup_w = -1
        # self.client_socket = -1
        # self.gui_update(self.gui_init)

    def cancel(self):
        print("try cancel server")
        self.ct.cancel()
        """Trigger the select() to wake up"""
        self.wakeup_w.send(b'\x00')  # Send a dummy byte

    def gui_update(self,func):
        self.queue.put(func)
        self.root.event_generate("<<CheckQueue>>")

    # def gui_init(self):
    #     self.frame = ttk.LabelFrame(self.root, text="Server")
    #     self.frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
    #     self.label = ttk.Label(self.frame, text="Counter from Thread 2: 0")
    #     self.label.pack(pady=10)
        
    #     self.button = ttk.Button(self.frame, text="Click Me", command=self.on_button_click)
    #     self.button.pack(pady=10)


    # def add_handler(self, handler):
    #     self.handler = handler

    def start(self):

        self.ct.reset()
        self.wakeup_r, self.wakeup_w = socket.socketpair()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:

            # print("OpenSSL version:", ssl.OPENSSL_VERSION)
            # print("Supported TLS versions:")

            # for version in ssl.TLSVersion:
            #     try:
            #         ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            #         ctx.minimum_version = version
            #         ctx.maximum_version = version
            #         print(f"  ✅ {version.name}")
            #     except ValueError:
            #         print(f"  ❌ {version.name} not supported")            

            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow reuse of address
            server_socket.bind((self.host, self.port))
            server_socket.listen(1)
            print(f"Server listening on {self.host}:{self.port}...")

            if self.tls:
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

                # Load server certificate and private key
                context.load_cert_chain(certfile=os.getenv("PLATFORM_CERT"), keyfile=os.getenv("PLATFORM_KEY"))

                # Require client certificate for mutual TLS
                context.verify_mode = ssl.CERT_REQUIRED

                # Load the CA certificate used to verify client certs
                context.load_verify_locations(cafile=os.getenv("CA_ROOT_CERT"))

                # Optional: restrict to TLS 1.3 only
                context.minimum_version = ssl.TLSVersion.TLSv1_3
                context.maximum_version = ssl.TLSVersion.TLSv1_3

                # wrap an existing socket with SSLContext
                server_socket = context.wrap_socket(server_socket, server_side=True)

            while not self.ct.is_canceled():
                # self.client_socket = -1
                print("Server waits for the next request on select")
                readable, _, _ = select.select([server_socket, self.wakeup_r], [], [])
                for sock in readable:
                    if sock is server_socket:
                        # when client don't have valid certificate, the server_socket.accept() will raise an exception
                        client_socket = None
                        try:
                            client_socket, client_address = server_socket.accept()
                            print(f"Connection from {client_address}")
                            self.handler(client_socket)
                        except ssl.SSLError as e:
                            print(f"SSL error: {e}")
                        except socket.error as e:
                            print(f"Socket Error: {e}")
                        except Exception as e:
                            print(f"Unexpected Error: {e}")
                        
                        finally:
                            if client_socket is None or client_socket.fileno() == -1:
                                print("No client socket to handle")
                                continue
                            if self.tls:
                                if isinstance(client_socket, ssl.SSLSocket):
                                    print("Client socket is an SSLSocket")
                                    # client_socket.shutdown(socket.SHUT_RDWR)
                                    client_socket.unwrap()

                            if client_socket.fileno() != -1:
                                client_socket.close()
            print("Server thread is stopping")
            self.wakeup_w.close()
            self.wakeup_r.close()