#!/usr/bin/env python3

import threading
import socket
import argparse
import os
import pickle
import time
from Crypto.Cipher import AES

class Send(threading.Thread):
    """
    Thread to handle sending. This thread's blocking call is the input
    that will be sent to the server. It is inactive until a user types
    something that they want to send.
    """

    def __init__(self, sock, name):
        super().__init__()          #initialize thread superclass
        self.sock = sock            #connected to the socket the client class is connected to,
                                    #   uses the socket to send the messages to the server
        self.name = name            #address of socket

    def run(self):
        key = b'Sixteen byte key'   #arbitrary key for testing purposes

        while True:
            message = input('{}: '.format(self.name))                   #e.g. 'Alice: <insert user input>' is the message
            cipher = AES.new(key, AES.MODE_EAX)                         #create AES object
            message_bytes = bytes(message, 'ascii')                     #transfer user input into bytes
            ciphertext, tag = cipher.encrypt_and_digest(message_bytes)  #encrypts the message into the ciphertext with MAC tag
            nonce = cipher.nonce                                        #nonce used to create cipher object on other end
            cipher_tuple = ((ciphertext, tag, nonce))                   #pack the data into a sendable tuple
            packed_tuple = pickle.dumps(cipher_tuple)                   #pickle the tuple so it can be sent through the socket

            # Type 'QUIT' to leave the chatroom
            if message == 'QUIT':
                self.sock.sendall('Server: {} has left the chat.'.format(self.name).encode('ascii'))
                break

            # Send message to server for broadcasting
            else:
                self.sock.sendall('{}: {}'.format(self.name, packed_tuple).encode('ascii'))

        print('\nQuitting...')
        self.sock.close()
        os._exit(0)

class Receive(threading.Thread):
    """
    Thread that handles getting data from the server, the blocking call
    is self.sock.recv. Whenever a message is received, this class decrypts its contents
    """

    def __init__(self, sock, name):
        super().__init__()          #initialize threading superclass
        self.sock = sock            #socket that client is connected to
        self.name = name            #address of sock

    def run(self):    
        key = b'Sixteen byte key'           #arbitrary key for testing purposes
        while True:
            message = self.sock.recv(1024)  #receives a 1024 byte message
            if message:
                print('\r{}\n{}: '.format(message, self.name), end = '')
                ciphertext, tag, nonce = pickle.loads(message)          #load the packed tuple
                cipher = AES.new(key, AES.MODE_EAX, nonce = nonce)      #create a corresponding AES object
                plaintext = cipher.decrypt(ciphertext)                  #decrypt the ciphertext, storing in plaintext
                try:
                    cipher.verify(tag)                                          #checks authenticity of message
                    print('\r{}\n{}: '.format(plaintext, self.name), end = '')  #prints message
                except:
                    print("Sender not authenticated, key incorrect or message corrupt. Quitting...") #if message is inauthentic
                    sys.exit(0)                                                                      #quit
            else:
                # Server has closed the socket, exit the program
                print('\nOh no, we have lost connection to the server!')
                print('\nQuitting...')
                self.sock.close()
                os._exit(0)

class Client:

    def __init__(self, host, port):
        self.host = host                                                #host and port passed into command line
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   #client socket object that connects to server

    def start(self):
        print('Trying to connect to {}:{}...'.format(self.host, self.port))     
        self.sock.connect((self.host, self.port))
        print('Successfully connected to {}:{}'.format(self.host, self.port))

        print()
        name = input('Your name: ')

        print()
        print('Welcome, {}! Getting ready to send and receive messages...'.format(name))

        # Create send and receive threads
        send = Send(self.sock, name)
        receive = Receive(self.sock, name)

        # Start send and receive threads
        send.start()
        receive.start()

        #self.sock.sendall('Server: {} has joined the chat. Say hi!'.format(name).encode('ascii'))
        print("\rAll set! Leave the chatroom anytime by typing 'QUIT'\n")
        print('{}: '.format(name), end = '')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Chatroom Server')
    parser.add_argument('host', help='Interface the server listens at')
    parser.add_argument('-p', metavar='PORT', type=int, default=1060,
                        help='TCP port (default 1060)')
    args = parser.parse_args()

    client = Client(args.host, args.p)
    client.start()
