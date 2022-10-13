import socket
import selectors
import types

# Internal modules
from data_structures import ClusterList
from clustering import staticLinkage
from communication import client
#from clustering import IncrementalClusterInput
#from clustering import DynamicClustering
#from centralDataStructure import ClusterList


class Server:
    def __init__(self, maxConnections):
        self.run = False
        ipv4 = socket.AF_INET
        tcp = socket.SOCK_STREAM
        self.server_socket = socket.socket(ipv4, tcp)
        self.selector = selectors.DefaultSelector()
        self.maxConnections = maxConnections
        self.connectedClients = []
        self.clusterlist = ClusterList.ClusterList()

    def shutdown(self):
        self.selector.close()
        self.server_socket.close()

    def setUpSocketOnCurrentMachine(self, port):
        # Initialise socket
        host = ''
        port = port        
        print("Socket successfully created")

        # Bind the socket to a port
        self.server_socket.bind((host, port))
        print("socket binded to %s" % (port))

        # put the socket into listening mode
        self.server_socket.listen(self.maxConnections)  
        print("socket is listening")
        self.server_socket.setblocking(False)
        self.selector.register(self.server_socket, selectors.EVENT_READ, data=None)

        return self.server_socket
        # Local socket setup complete

    def clientSend(c, message):
        message = str(message)
        encoded = message.encode()
        c.send(encoded)

    def receives(c):
        rMessage = c.recv(1024)
        return rMessage.decode()

    def receive(c, buffer):
        rMessage = c.recv(buffer)
        return rMessage.decode()
        
    def acceptNewConnection(self, socket):
        # Establish connection with a client.
        client_socket, client_addr = socket.accept()
        print('Got connection from', client_addr)
        # Disable blocking to preventthe server waiting until socket returns data.
        client_socket.setblocking(False)
        data = types.SimpleNamespace(addr=client_addr,inb=b"",outb=b"")        
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        # Pass socket and events mask to register
        self.selector.register(client_socket, events, data=data)
        # Create new client object with a unique id     
        id = self.assignId(client_addr)
        if id:
            newClient = client.client(client_socket, client_addr, self, clientIdentifier=id)
        else:
            newClient = client.client(client_socket, client_addr, self)
        self.connectedClients.append(newClient)

    def launchServer(self):
        # a forever loop until we interrupt it or an error occurs
        self.run = True        
        while self.run:
            events = self.selector.select(timeout=200)
            for key, mask in events:
                if key.data is None:
                    self.acceptNewConnection(key.fileobj)
                else:
                    self.serve_client(key, mask)

    def serve_client(self,key, mask):
        connSocket = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            rcvd = Server.receive(connSocket, 1024)
            if rcvd:
                # print("RECEIVED:", rcvd)
                # To-do": Figure out a better way for the server to display information than printing every received message.
                # ie metrics.display()
                for connClient in self.connectedClients:
                    if connClient.socket == connSocket:
                        connClient.interpretMessage(rcvd)                        
            else:
                print("Closing connection to: ", mask)
                self.selector.unregister(connSocket)
                connSocket.close()     
        if mask & selectors.EVENT_WRITE:
            if data.outb:
                print(f"Echoing {data.outb!r} to {data.addr}")
                sent = connSocket.send(data.outb)  # Should be ready to write
                data.outb = data.outb[sent:]                             
                
    def assignId(self, clientaddress, checkPreviousConnections=False):
        # assign a number to the client based on it's address
        # Priority 1: Assign a new number to every new connection
        # Priority 2: Store a list that correlates connection address and identifier to reuse identifier - can store in txt for now
        id = 0
        foundPrevious = False
        if checkPreviousConnections:            
            # Use connections.txt (storing in format of "address:clientId \n")

            # for lines in conn.txt
                # previousConnection = readline(connections.txt)
                # storedAddress, storedClientId = previousConnection.split(":")
                # looking for a previous connection with the same address
                # if clientaddress == storedAddress
                    # id = storedClientId
                    # foundPrevious = True
            pass
        if not foundPrevious:
            id = self.findHighestId()
        print("ASSIGNED ID:",id)
        return id

    def findHighestId(self):
        highestId = 0 
        # Check id's currently in use and find the highest one.
        for c in self.connectedClients:
            if c.clientId > highestId:
                highestId = c.clientId
        # Found highest id, now add 1 to it and assign it to the new connection.
        highestId += 1
        id = highestId
        return id


    def doStaticLinkage(self, json=False):
        # Perform hungarian algorithm on 3 inputs

        # Purpose of this function is for demonstration, we will be using first 3 
        # databases as a staticly linked starting point then add 2 more dynamically

        # Input should be all 3 clients records who have sent operation STATIC INSERT.
        if json:
            for clients in self.connectedClients:
                # find 3 clients
                # make a list of records that are stored as format [rowId, concatenated encodings]
                # pass to db1/2/3 parameters
                pass
        else:
            foundDb = 0
            for clients in self.connectedClients:
                assert clients.encodedRecords != None
                if foundDb == 0:
                    db1 = clients.encodedRecords
                    foundDb += 1
                if foundDb == 1:
                    db2 = clients.encodedRecords
                    foundDb += 1
                if foundDb == 2:
                    db3 = clients.encodedRecords              
            

        # Static linkage with 3 databases
        staticLinkage.staticLinkage(db1, db2, db3)

    def staticLinkageFormatting(self):
        pass

    def doDynamicLinkage(self):
        # Update clusters
        pass              
            

def main():
    # Program parameter: maxConnections (default of 5, optional)
    # Program parameter: port
    # Usage: server.py port maxConnections    

    server = Server(15)
    server_socket = server.setUpSocketOnCurrentMachine(43555)
    server.launchServer()
    server.shutdown()


if __name__ == "__main__":
    main()


