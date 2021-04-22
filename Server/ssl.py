import socket
import json
import random




HOST = '127.0.0.1' 
PORT = 1024
PRIVATEKEY = '987654321'

def sendDefaultResponse(sock, client):
    print('authentication failed')
    client.sendall('ERR: AUTHENTICATION FAILED'.encode())
    sock.close()




def sendPrivateKey(sock, client):
    with client:
    # Here we should encrypt private key with the public key sent by client
        client.sendall(PRIVATEKEY.encode())
        while True: 
            data = client.recv(1024)
            if not data: 
                break
            
            msg = json.loads(data.decode())
            print('received data:', msg)

            if 'decrypted key' in msg.keys():
                #client.sendall('decrypted key received'.encode())
                if msg['decrypted key'] == PRIVATEKEY:
                    authenticate(sock, client)
                else:
                    print('wrong private key received')
                    sendDefaultResponse(sock, client)
                break
            else:
                print('decrypted key not recieved')
                sendDefaultResponse(sock, client)
                break



def authenticate(sock, client):
    with client:
    # Here we should encrypt private key with the public key sent by client
        print('authenticated!')
        client.sendall('Authenticated!'.encode())

#opening a listening socket on port, listening for clients to connect


if __name__ == '__main__':

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        client, addr = s.accept()
        with client:
            print("Client connected by: ", addr)
            while True: 
                data = client.recv(1024)
                if not data: 
                    break
                
                
                msg = json.loads(data.decode())
                print('received data:', msg)
                if 'public key' in msg.keys():
                    #client.sendall('public key received'.encode())
                    sendPrivateKey(s, client)
                    break
                else:
                    print('public key not recieved')
                    sendDefaultResponse(s, client)
                    break
                

                client.sendall(data)




