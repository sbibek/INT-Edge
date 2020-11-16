import threading
from queryhandler import QueryHandler
import pickle
import struct

class MetaClientProcessor(threading.Thread):
    def __init__(self, connection, address, processor):
        threading.Thread.__init__(self)
        self.connection = connection
        self.queryhandler = QueryHandler(processor)

    def run(self):
        data = pickle.dumps(self.queryhandler.rank(1))
        lenInfo = struct.pack(">I", len(data))
        self.connection.sendall(lenInfo)
        self.connection.sendall(data)
        self.connection.close()
    
    def recvExactly(socket, n):
        recvPayload = b""
        remainingPayload = n
        while remainingPayload != 0:
            recvPayload += socket.recv(remainingPayload)
            remainingPayload = n - len(recvPayload)
        return recvPayload