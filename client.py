import socket
import pickle
from Crypto.Cipher import AES

HEADERSIZE = 10

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostname(), 1235))
#connect to server
key = b'Sixteen byte key'


while True:
    
    full_msg = b''
    new_msg = True;
    while True:
        msg = s.recv(16)    #buffer of 16 bytes at a time
        if new_msg:
            print(f"new message length: {msg[:HEADERSIZE]}")
            msglen = int(msg[:HEADERSIZE])
            new_msg = False
            
        full_msg += msg

        if len(full_msg)-HEADERSIZE == msglen:
            print("full msg recvd")
            print(full_msg[HEADERSIZE:])

            #receive transmitted nonce once all data comes in
            ciphertext, tag, nonce = pickle.loads(full_msg[HEADERSIZE:])
            #create corresponding AES object
            cipher = AES.new(key, AES.MODE_EAX, nonce = nonce)
            plaintext = cipher.decrypt(ciphertext)

            try:
                cipher.verify(tag)
                print("the message is authentic: ", plaintext)
            except:
                print("Key incorrect or message corrupted")
            
            
            new_msg = True
            full_msg = b''

