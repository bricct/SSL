import socket
import json
from src.Encryption.encryption import encrypt, decrypt
from src.Encryption.key_gen import key_gen
from src.Encryption.hmac import hmac

HOST = '127.0.0.1'
PORT = 1024

dev = 0

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
    print('\twithdrw <amount>\twithdraws money from account')
    print('\tlogout\t\t\tlogs out of the current session')
    print('\texit\t\t\texits the interface')
    print('\tquit\t\t\tforce quits the interface')


def formatMsg(msg, token):
    msg_len = min(len(msg), 32)
    msg = msg[:msg_len]
    #print(msg)
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
    
    if function == 'deposit' or function == 'withdrw':
        return {'request' : function, 'amount' : args[1], 'token' : token}
    else:
        return {'request' : function, 'token' : token}
    

def decryptAndVerifyMsg(msg, key):
    decRes = decrypt(data.decode(), PRIVATEKEY, N)
    decMsgJson = json.loads(decRes)
    decMsg = ''
    if 'msg' and 'hmac' in decMsgJson.keys():
        decMsg = decMsgJson['msg']
        sMac = decMsgJson['hmac']
        if hmac(SERVERPUBLICKEY, decMsg) != sMac:
            decMsg = 'Message from server corrupted'
            if dev:
                print(hmac(SERVERPUBLICKEY, decMsg) + ' != ' + sMac)
        else:
            if dev:
                print(hmac(SERVERPUBLICKEY, decMsg) + ' == ' + sMac)
    else:
        decMsg = 'Message from server corrupted'

    return decMsg


if __name__ == '__main__':

    PRIVATEKEY, PUBLICKEY, N = key_gen()

    print('Private key', PRIVATEKEY)
    print('Public key', PUBLICKEY)
    print('N', N)

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
        if dev:
            print('decoded msg', data.decode())
            print('decrypted n', decrypt(data.decode(), PRIVATEKEY, N))
        SERVERN = int(decrypt(data.decode(), PRIVATEKEY, N))



        d_key = {'decrypted key' : str(SERVERPUBLICKEY)}

        msg = encrypt(json.dumps(d_key), SERVERPUBLICKEY, SERVERN)
        if dev:
            print('sending decrypted key')
            print(d_key, end = '\n\n')

        s.send(msg.encode())

        data = s.recv(2048)

        decMsg = decryptAndVerifyMsg(data, SERVERPUBLICKEY)

        #if dev:

        print('Received: ', decMsg)

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
            mac = hmac(PUBLICKEY, request)
            fullRequest = json.dumps({'msg' : request, 'hmac' : mac})
            encReq = encrypt(fullRequest, SERVERPUBLICKEY, SERVERN)

            s.send(encReq.encode())
            data = s.recv(4096)

            if dev:
                print(data.decode())
            if data.decode():
                decMsg = decryptAndVerifyMsg(data, SERVERPUBLICKEY)

            else:
                decMsg = ''

            if msg == 'exit':
                break
            if msg.split()[0] == 'login':
                token = decMsg
                data = s.recv(4096)
                decMsg = decryptAndVerifyMsg(data, SERVERPUBLICKEY)

            print(decMsg)

            
