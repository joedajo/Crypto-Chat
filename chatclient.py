import socket
import threading
import argparse
import os

class Send(threading.Thread):

    #Send constructor
    def __init__(self, sock, name):
        super().__init__()
        self.sock = sock
        self.name = name

    def run(self):

        while True:
            #Input for user to type in
            message = input('{}: '.format(self.name))

            #User can quit by typing 'quit'
            if message == 'quit':
                self.sock.sendall('Server: {} has left the chat.'.format(self.name).encode('ascii'))
                break

            else:
                self.sock.sendall('{}: {}'.format(self.name, message).encode('ascii'))

        print('\nQuitting...')
        self.sock.close()
        os._exit(0)


class Receive(threading.Thread):

    #Constructor for receiving
    def __init__(self, sock, name):

        super().__init__()
        self.sock = sock
        self.name = name

    def run(self):

        while True:
            #Retreiving the message with a buffer size of 1024
            message = self.sock.recv(1024)
            if message:
                print('\r{}\n{}: '.format(message.decode('ascii'), self.name), end = '')

            else:
                print('\nConnection has been lost to the server!')
                print('\nQuitting...')
                self.sock.close()
                os_exit(0)


class Client:

    #Defining the constructor
    def __init__(self, host, port):

        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self):

        print('Trying to connect{}:{}'.format(self.host, self.port))
        self.sock.connect((self.host, self.port))
        print('Successfull connected to {}:{}'.format(self.host, self.port))

        #Getting the user's name
        print()
        username = input('Type in your username: ')

        print()
        print('Welcome, {}! Getting ready to send and receive messages...'.format(username))

        #Allows for sending and receiving threads
        send = Send(self.sock, username)
        receive = Receive(self.sock, username)

        send.start()
        receive.start()

        #Lets chat know who joined the server
        self.sock.sendall('Server: {} has joined the chat!'.format(username).encode('ascii'))
        print("\rAll set! To leave the chatroom type 'quit'\n")
        print('{}: '.format(username), end = '')
        


#Arguments when running the program
if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Chatroom Server')
    parser.add_argument('host', help='Interface the server listens at')
    parser.add_argument('-p', metavar='PORT', type=int, default=1606, help='TCP port (default 1606)')
    args = parser.parse_args()

client = Client(args.host, args.p)
client.start()

        
