import socket
import json
from src.Encryption.encryption import encrypt, decrypt
from src.Encryption.key_gen import key_gen

HOST = '127.0.0.1'
PORT = 1024

dev = 1

PUBLICKEY = ''
PRIVATEKEY = ''
N = ''

SERVERPUBLICKEY = ''
SERVERPRIVATEKEY = ''
SERVERN = ''


def printHelp():
    print('COMMAND LIST:')
    print('\thelp\t\t\tdisplays command list')
    print('\tlogin <user> <pass>\tallows login to remote server')
    print('\tbalance \t\tdisplays balance of account')
    print('\tdeposit <amount>\tdeposits money to account')
    print('\twithdraw <amount>\twithdraws money from account')
    print('\tlogout\t\t\tlogs out of the current session')
    print('\texit\t\t\texits the interface')
    print('\tquit\t\t\tforce quits the interface')


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
    


if __name__ == '__main__':

    PRIVATEKEY, PUBLICKEY, N = key_gen()


    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        s.connect((HOST, PORT))

        if dev:
            print('sending public key')
            print(PUBLICKEY, end = '\n\n')

        s.send(json.dumps({'public key' : str(PUBLICKEY), 'N' : str(N)}).encode())
        data = s.recv(1024)

        if dev:
            print('received encrypted key')
            print(data.decode(), end = '\n\n')
            print('hey')

        SERVERPUBLICKEY = int(decrypt(data.decode(), PRIVATEKEY, N))
        data = s.recv(1024)
        SERVERN = decrypt(int(data.decode()), PRIVATEKEY, N)



        d_key = {'decrypted key' : encrypt(str(SERVERPUBLICKEY), SERVERPUBLICKEY, SERVERN)}


        if dev:
            print('sending decrypted key')
            print(d_key, end = '\n\n')

        s.send(json.dumps(d_key).encode())

        data = s.recv(1024)
        
        msg = decrypt(data.decode(), PRIVATEKEY, N)


        print('Received: ', msg)

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

            
