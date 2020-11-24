import socket
import time
import pickle
from Crypto.Cipher import AES

HEADERSIZE = 10

#key and AES object
key = b'Sixteen byte key'
cipher = AES.new(key, AES.MODE_EAX)

#Encryption--------------------------------------
#data to be encrypted
data = b"joe"

#create tuple with ciphertext and MAC
ciphertext, tag = cipher.encrypt_and_digest(data)

#Nonce used in transmission
nonce = cipher.nonce

#tuple that will be sent to client
d = ((ciphertext, tag, nonce))

#pack tuple so it can be sent as one to client
msg = pickle.dumps(d)
#------------------------------------------------

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#AF_INET corresponds to IPv4
#SOCK_STREAM means we will be using TCP

s.bind((socket.gethostname(), 1235))
#hosting server on our machine, thats why gethostname
#1234 is port number

s.listen(5)
#leaves a queue of 5 to receive

while True:
    clientsocket, address = s.accept() #clientsocket is another socket object
    print(f"connection from {address} has been esablished!")

    msg = bytes(f'{len(msg):<{HEADERSIZE}}', "utf-8") + msg
    #the < above means left align

    clientsocket.send( msg )

