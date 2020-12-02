#!/usr/bin/env python3

import threading
import socket
import argparse
import os
import json
import time
from Crypto.Cipher import AES
from base64 import b64encode
from base64 import b64decode
from Crypto.Random import get_random_bytes

HEADERSIZE = 10

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
            message = input('{}: '.format(self.name))
            cipher = AES.new(key, AES.MODE_EAX)                         #create AES object
            message_bytes = bytes(message, 'ascii')                     #transfer user input into bytes
            ciphertext, tag = cipher.encrypt_and_digest(message_bytes)
            nonce = cipher.nonce
            json_k = [ 'nonce', 'ciphertext', 'tag' ]
            json_v = [ b64encode(x).decode('utf-8') for x in [cipher.nonce, ciphertext, tag]]
            result = json.dumps(dict(zip(json_k, json_v)))
            print(result)
            msg = bytes(result, 'ascii')

            # Type 'QUIT' to leave the chatroom
            if message == 'QUIT':
                self.sock.sendall('Server: {} has left the chat.'.format(self.name).encode('ascii'))
                break

            # Send message to server for broadcasting
            else:
                #formatted_msg = ('{}: {}'.format(self.name, packed_tuple).encode('ascii'))
                #formatted_msg = bytes(f'{len(packed_tuple):<{HEADERSIZE}}', "ascii") + packed_tuple
    
                self.sock.sendall(msg)

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
            message = self.sock.recv(1024)
            try:
                b64 = json.loads(message)
                json_k = [ 'nonce', 'ciphertext', 'tag' ]
                jv = {k:b64decode(b64[k]) for k in json_k}
                cipher = AES.new(key, AES.MODE_GCM, nonce=jv['nonce'])
                plaintext = cipher.decrypt_and_verify(jv['ciphertext'], jv['tag'])
                print("The message was: " + plaintext)
            except:
                print("Incorrect decryption")
          
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
