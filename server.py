import ssl
import socket

ca_root_cert  = "/certs/ca.crt"         # for client validation
platform_cert = "/certs/platform.crt"   # client/server certificate
platform_key  = "/certs/platform.key"   # client/server certificate private key

class server:
    def __init__(self, host="0.0.0.0", port=12123, tls=True):
        self.host = host
        self.port = port
        self.tls = tls
        # self.handler = handler
        self.client_socket = 0

    def add_handler(self, handler):
        self.handler = handler

    def start(self):

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

            if self.tls:
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

                # Load server certificate and private key
                context.load_cert_chain(certfile=platform_cert, keyfile=platform_key)

                # Require client certificate for mutual TLS
                context.verify_mode = ssl.CERT_REQUIRED

                # Load the CA certificate used to verify client certs
                context.load_verify_locations(cafile=ca_root_cert)

                # Optional: restrict to TLS 1.3 only
                context.minimum_version = ssl.TLSVersion.TLSv1_3
                context.maximum_version = ssl.TLSVersion.TLSv1_3

                # wrap an existing socket with SSLContext
                server_socket = context.wrap_socket(server_socket)

            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow reuse of address
            server_socket.bind((self.host, self.port))
            server_socket.listen(1)
            print(f"Server listening on {self.host}:{self.port}...")

            while True:
                client_socket, client_address = server_socket.accept()
                print(f"Connection from {client_address}")
                self.handler(client_socket)
                print("Server waits for the next request") 