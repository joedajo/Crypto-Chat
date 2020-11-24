import socket
import time
import pickle


HEADERSIZE = 10

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
    
    d = {1: "Hey", 2: "There"}
    msg = pickle.dumps(d)

    msg = bytes(f'{len(msg):<{HEADERSIZE}}', "utf-8") + msg
    #the < above means left align

    clientsocket.send( msg )

