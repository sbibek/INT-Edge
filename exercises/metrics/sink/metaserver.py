import threading
import socket
from metaclientprocessor import MetaClientProcessor
from conf import conf

class MetaServer(threading.Thread):
    def __init__(self, processor):
        threading.Thread.__init__(self)
        self.port = conf.getMetaServerConf()['port']
        self.host = "0.0.0.0"
        self.processor = processor
    
    def run(self):
        self.serve()

    def serve(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        try:
            while True:
                print("[metaserver] starting worker instance at ({},{})".format(self.host, self.port))
                server.listen()
                connection, address = server.accept()
                print("[metaserver] got connection from {}", address)
                inv = MetaClientProcessor(connection,address, self.processor)
                inv.start()
                # now return to listening for more connections
        except KeyboardInterrupt as e:
            raise e