#!/usr/bin/env python3

import threading
import socket
import argparse
import os
import json
import time
import random
import math
import hashlib
import binascii
import sys
from Crypto.Cipher import AES
from base64 import b64encode
from base64 import b64decode
from Crypto.Random import get_random_bytes
from Crypto.Hash import HMAC, SHA256

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
        #key = bytes(password, 'utf-8')   #arbitrary key for testing purposes
        while True:
            message = input('{}: '.format(self.name))
            cipher = AES.new(key, AES.MODE_EAX)                         #create AES object
            message_bytes = bytes(message, 'utf-8')                     #transfer user input into bytes
            ciphertext, tag = cipher.encrypt_and_digest(message_bytes)
            nonce = cipher.nonce
            json_k = [ 'name', 'nonce', 'ciphertext', 'tag' ]
            json_v = [ b64encode(x).decode('utf-8') for x in (bytes(self.name, 'utf-8'), cipher.nonce, ciphertext, tag)]
            result = json.dumps(dict(zip(json_k, json_v)))
            print(result)
            msg = bytes(result, 'utf-8')

            # Type 'QUIT' to leave the chatroom
            if message == 'QUIT':
                self.sock.sendall('Server: {} has left the chat.'.format(self.name).encode('utf-8'))
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
        #key = bytes(password, 'utf-8')        #arbitrary key for testing purposes
        while True:
            message = self.sock.recv(1024)
            try:
                b64 = json.loads(message)
                json_k = [ 'name', 'nonce', 'ciphertext', 'tag' ]
                jv = {k:b64decode(b64[k]) for k in json_k}
                cipher = AES.new(key, AES.MODE_EAX, nonce=jv['nonce'])
                plaintext = cipher.decrypt_and_verify(jv['ciphertext'], jv['tag'])
                print(f"\n{jv['name'].decode('utf-8')}: " + plaintext.decode('utf-8'))
            except (ValueError, KeyError):
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

        self.id = int(self.sock.recv(8))
        timestamp = int(math.ceil(time.time()))
        timestamp = int(timestamp/100)
        random.seed(math.ceil(timestamp))
        rand1 = random.getrandbits(64)
        rand2 = random.getrandbits(64)
        global key
        key = (random.getrandbits(64).to_bytes(16, byteorder='big')) + bytes(password, 'utf-8')
        if(self.id == 0):
            tohash = password + str(timestamp ^ rand1)
            toverify = password + str(timestamp ^ rand2)
            tohash = bytes(tohash, 'utf-8')
            toverify = bytes(toverify, 'utf-8')
            #send hash(key|timestamp+rand_1)
            hash_object1 = hashlib.pbkdf2_hmac('sha256', tohash, b'salt', 100000)
            hash_object2 = hashlib.pbkdf2_hmac('sha256', toverify, b'salt', 100000)
            print('Challenge: ', binascii.hexlify(hash_object1))
            print('Response should match: ', binascii.hexlify(hash_object2))
            time.sleep(10)
            self.sock.send(binascii.hexlify(hash_object1))
            #recv other hash
            msg_to_verify = self.sock.recv(1024)
            #verify hash
            if msg_to_verify == binascii.hexlify(hash_object2):
                print('Success, chat session authenticated')
                print('Response: ', msg_to_verify)
            else:
                print('Failure to authenticate. Quitting...')
                sys.exit(0)
        else:
            tohash = password + str(timestamp ^ rand2)
            toverify = password + str(timestamp ^ rand1)
            #send hash(key|timestamp+rand_2)
            tohash = bytes(tohash, 'utf-8')
            toverify = bytes(toverify, 'utf-8')
            hash_object1 = hashlib.pbkdf2_hmac('sha256', tohash, b'salt', 100000)
            hash_object2 = hashlib.pbkdf2_hmac('sha256', toverify, b'salt', 100000)
            print('Challenge: ', binascii.hexlify(hash_object1))
            print('Response should match: ', binascii.hexlify(hash_object2))
            self.sock.send(binascii.hexlify(hash_object1))
            #recv other hash
            msg_to_verify = self.sock.recv(1024)
            #verify hash
            if msg_to_verify == binascii.hexlify(hash_object2):
                print('Success, chat session authenticated')
                print('Response: ', msg_to_verify)
            else:
                print('Failure to authenticate. Quitting...')
                sys.exit(0)
        print()
        name = input('Your name: ')

        print()
        print('Welcome, {}! Getting ready to send and receive messages...'.format(name))
        print('Client ID: ', self.id)

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
    parser.add_argument('password', help='Password you share with the other user')
    parser.add_argument('-p', metavar='PORT', type=int, default=1060,
                        help='TCP port (default 1060)')
    args = parser.parse_args()
    
    global password
    password = args.password
    global key
    client = Client(args.host, args.p)
    client.start()
