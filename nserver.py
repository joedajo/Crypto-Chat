#!/usr/bin/env python3

import threading
import socket
import argparse
import os

HEADERSIZE = 10

class Server(threading.Thread):

    def __init__(self, host, port):
        super().__init__()          #initializes thread superclass constructor
        self.connections = []       #list of all sockets the server is connected to
        self.host = host            #host and port are passed in in the main function,
        self.port = port            #   through command line arguments

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    #creates server socket using internet addr family & TCP
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  #makes it so the socket can be reused at the specified port
        sock.bind((self.host, self.port))                           #binds the server socket to the host & port

        sock.listen(1)                              #listens for 1 (?) connection at a time... queue?
        print('Listening at ', sock.getsockname())  #prints the IP address and port server is active on

        while True:
            #Accept new connection
            #sc is the new socket that is connected from this server to
            #   the client, sockname is the address of the client
            sc, sockname = sock.accept()    
            print(f'Accepted a new connection from {sc.getpeername()} to {sc.getsockname()}.')
            sc.send(bytes(str(len(self.connections)), 'utf-8'))

            #Create new thread
            server_socket = ServerSocket(sc, sockname, self)

            #Start new thread
            server_socket.start()

            #Add thread to active connections
            self.connections.append(server_socket)
            print('Ready to receive messages from', sc.getpeername())
            
    def broadcast(self, message, source):
        """
        Sends a message to all connected clients, except the source of the message.
        Args:
            message (str): The message to broadcast.
            source (tuple): The socket address of the source client.
        """
        for connection in self.connections:

            # Send to all connected clients except the source client
            if connection.sockname != source:
                connection.send(message)
    
    def remove_connection(self, connection):
        """
        Removes a ServerSocket thread from the connections attribute.
        Args:
            connection (ServerSocket): The ServerSocket thread to remove.
        """
        self.connections.remove(connection)



#facilitates communications with individual sockets
class ServerSocket(threading.Thread):

    def __init__(self, sc, sockname, server):
        super().__init__()                      #initializes threading superclass obj
        self.sc = sc                            #this ServerSocket object is tied to the client that the server connected to 
        self.sockname = sockname                #address of sc
        self.server = server                    #server object that the client is connected to 

    def run(self):
        while True:
            message = self.sc.recv(1024)                   #server waits to receive a message of 1024 bytes
            if message:                                                     #if the message isnt empty
                print('{} says {!r}'.format(self.sockname, message))        #prints on server cmd line who said what
                self.server.broadcast(message, self.sockname)               #broadcasts the message to all other clients
            else:
                # Client has closed the socket, exit the thread
                print('{} has closed the connection'.format(self.sockname))
                self.sc.close()
                server.remove_connection(self)
                return

    def send(self, message):
        self.sc.sendall(message)    #sends the message passed in through the socket connected to the client


def exit(server):
    """
    Allows the administrator to close the server if they type q in the cmd line
    """
    while True:
        ipt = input('')
        if ipt == 'q':
            print('Closing all connections...')
            for connection in server.connections:
                connection.sc.close()
            print('Shutting down the server...')
            os._exit(0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Chatroom Server')
    parser.add_argument('host', help='Interface the server listens at')
    parser.add_argument('-p', metavar='PORT', type=int, default=1060,
                        help='TCP port (default 1060)')
    args = parser.parse_args()

    # Create and start server thread
    server = Server(args.host, args.p)
    server.start()

    exit = threading.Thread(target = exit, args = (server,))
    exit.start()
