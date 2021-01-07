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
        # lets get the swid first
        swid = struct.unpack('>I', self.recvExactly(self.connection, 4))[0]
        print("[mcp] serving rank query for swid {}".format(swid))
        data = pickle.dumps(self.queryhandler.rankII(swid))
        lenInfo = struct.pack(">I", len(data))
        self.connection.sendall(lenInfo)
        self.connection.sendall(data)
        self.connection.close()
    
    def recvExactly(self,socket, n):
        recvPayload = b""
        remainingPayload = n
        while remainingPayload != 0:
            recvPayload += socket.recv(remainingPayload)
            remainingPayload = n - len(recvPayload)
        return recvPayload