import socket
import json
HOST = '127.0.0.1'
PORT = 1024

p_key = {'public key' : '12345'}

dev = 1

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    
    s.connect((HOST, PORT))

    if dev:
        print('sending private key')
        print(p_key, end = '\n\n')

    s.send(json.dumps(p_key).encode())
    data = s.recv(1024)

    if dev:
        print('received encrypted key')
        print(data.decode(), end = '\n\n')

    d_key = {'decrypted key' : data.decode()}


    if dev:
        print('sending decrypted key')
        print(d_key, end = '\n\n')

    s.send(json.dumps(d_key).encode())

    data = s.recv(1024)
    

print('Received: ', data.decode())




