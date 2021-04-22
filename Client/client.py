import socket
import json
HOST = '127.0.0.1'
PORT = 1024

p_key = {'public key' : '12345'}

dev = 1


def printHelp():
    pass

def formatMsg(msg, token):
    args = msg.split()
    function = args[0]
    if function == 'login':
        if len(args) < 3:
            print('ERR: USAGE "login <user> <pass>"')
            return False
        else:
            user = args[1]
            passw = args[2]
            return {'request' : function, 'user' : user, 'pass' : passw}
    
    if function == 'deposit' or function == 'withdraw':
        return {'request' : function, 'amount' : args[1], 'token' : token}
    else:
        return {'request' : function, 'token' : token}
    




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

    token = ''

    while True:
        msg = input(">>> ")
        if not msg:
            continue
        if msg == 'help':
            printHelp()
            continue
        if msg == 'quit':
            break

        res = formatMsg(msg, token)
        if not res:
            continue

        request = json.dumps(res)
        

        s.send(request.encode())
        data = s.recv(1024)
        if msg == 'exit':
            break
        if msg.split()[0] == 'login':
            token = data.decode()
            data = s.recv(1024)
        print(data.decode())

        
