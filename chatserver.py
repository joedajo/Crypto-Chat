'''
Server for Chatroom
'''

import socket
import threading
import argparse
import os

class Server(threading.Thread):

    #defining the constructor
    def __init__(self, host, port):
        super().__init__()
        self.connections = []
        self.host = host
        self.port = port

 
    def run(self):

        #Using IPv4 as well as TCP
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))

        #Listening for new connections
        sock.listen(1)
        print('Listening at ', sock.getsockname())

        while True:

            #Accepting new connections
            conn, addr = sock.accept()
            print('Accepted a new connection from {} to {}'.format(conn.getpeername(), conn.getsockname()))

            #Creating a new thread
            server_socket = ServerSocket(conn, addr, self)

            #Starting the new thread
            server_socket.start()

            #Adding the thread to a list of active connections
            self.connections.append(server_socket)
            print('Ready to recieve messages from ', conn.getpeername())


    def broadcast(self, message, source):

        for connection in self.connections:

            #Sending message to everyone except the sender
            if connection.addr != source:
                connection.send(message)


class ServerSocket(threading.Thread):

    #Defining the constructor
    def __init__(self, conn, addr, server):
        super().__init__()
        self.conn = conn
        self.addr= addr
        self.server = server


    def run(self):

        while True:

            message = self.conn.recv(1024).decode('ascii')
            if message:
                print('{} says {!r}'.format(self.addr, message))
                self.server.broadcast(message, self.addr)

            else:

                print('{} has closed the connection'.format(self.addr))
                self.conn.close()
                server.remove_connection(self)
                return

    def send(self, message):
        self.conn.sendall(message.encode('ascii'))


def exit(server):

    #To close the server type 'quit'
    while True:
        temp = input('')
        if temp == 'quit':
             print('Closing all connnections...')
             for connection in server.connections:
                connection.conn.close()
             print('Shutting down the server...')
             os._exit(0)

#Arguments for running the program
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Chatroom Server')
    parser.add_argument('host', help='Interface the server listens at')
    parser.add_argument('-p', metavar='PORT', type=int, default=1606, help='TCP port (default 1606)')
    args = parser.parse_args()

    server = Server(args.host, args.p)
    server.start()

    exit = threading.Thread(target = exit, args = (server,))
    exit.start()




        
    
