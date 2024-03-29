import socket
import json
import random
import pandas as pd
from secrets import token_hex
import time
#import sys
#sys.path.append('..')
from src.Encryption.encryption import encrypt, decrypt
from src.Encryption.key_gen import key_gen
from src.Encryption.hmac import hmac

HOST = '127.0.0.1' 
PORT = 1024

# THIS KEY IS A PLACEHOLDER, IT SHOULD BE REPLACED WHEN WE INTEGRATE ENCRYPTION

PUBLICKEY = ''
PRIVATEKEY = ''
N = ''

CLIENTPUBLICKEY = ''
CLIENTPRIVATEKEY = ''
CLIENTN = ''

PATHTOCSV = 'src/Server/Data/data.csv'

dev = 1


## Default responses from the server to the client

def sendDefaultResponse(sock, client):
    print('authentication failed')
    client.send('ERR: AUTHENTICATION FAILED'.encode())
    sock.close()

def sendBadRequestResponse(sock, client, message):
    print('Bad Request received from client', message)
    sendMsg(sock, client, 'ERR: BAD/CORRUPTED REQUEST, TYPE HELP FOR LIST OF COMMANDS AND USAGE')

def sendLoginResponse(sock, client):
    print('Bad Request received, client is not logged in')
    sendMsg(sock, client, 'ERR: YOU ARE NOT LOGGED IN, PLEASE LOG IN TO MAKE REQUESTS TO THE SERVER')

def sendBadLoginResponse(sock, client):
    print('Bad Login received')
    sendMsg(sock, client, 'null')
    sendMsg(sock, client, 'ERR: BAD LOGIN, THAT COMBINATION OF USER AND PASSWORD IS NOT FOUND IN OUR DATABASE')

def sendBadTokenResponse(sock, client):
    print('Bad Token received')
    sendMsg(sock, client, 'ERR: SESSION ENDED, PLEASE LOG IN AGAIN')






## SENDS ENCRYPTED RESPONSE TO THE CLIENT
def sendMsg(sock, client, msg):

    # encrypt message with clients public key
    mac = hmac(PUBLICKEY, msg)
    msgJson = json.dumps({'msg' : msg, 'hmac' : mac})
    encMsg = encrypt(msgJson, CLIENTPUBLICKEY, CLIENTN)
    client.send(encMsg.encode())
    print('sent message to client')


def recvMsg(sock, client):

    data = client.recv(4096)
    decData = decrypt(data.decode(), PRIVATEKEY, N)
    decMsg = {'request' : 'bad'}
    try:
        decJson = json.loads(decData)
        decMsg = json.loads(decJson['msg'])
        #print('found a message', decMsg)
        decHmac = decJson['hmac']
        
        #print('found an hmac')
        #print(type(decHmac))
        if decHmac != hmac(CLIENTPUBLICKEY, json.dumps(decMsg)):

            print(decHmac + ' != ' +  hmac(CLIENTPUBLICKEY, json.dumps(decMsg)))
            print('Message authentication failed')
            if decMsg['request'] == 'login':
                return json.dumps({'request' : 'login'})
            
            return 'Bad'
        else:
            if dev:
                print(decHmac + ' == ' +  hmac(CLIENTPUBLICKEY, json.dumps(decMsg)))
    except:
        print('Invalid message received')
        if decMsg['request'] == 'login':
            return json.dumps({'request' : 'login'})
        return 'Bad'


    return json.dumps(decMsg)


def getUserFromToken(token, df):
    row = df.loc[df['Token'] == token]

    # Check if token is real
    if len(row) < 1:
        return False
    
    else:

        # Check if token is expired
        if row['Expires'].item() < int(time.time()):
            return False

        else:    
            return row['User'].item()

def updateToken(user, df):
    df.loc[df['User'] == user, ['Expires']] = int(time.time()) + 900

def sendLogin(sock, client, msg, df):
   
    user = msg['user']
    passw = msg['pass']

    row = df.loc[df['User'] == user]
    
    if len(row) < 1:
        sendBadLoginResponse(sock, client)
        return
    
    else:
        if row['Pass'].item() == passw:

            newToken = token_hex(16)
            df.loc[df['User'] == user, ['Token']] = newToken
            updateToken(user, df)
            sendMsg(sock, client, newToken)
            sendMsg(sock, client, 'Welcome back ' + user + '!')
            saveState(df)
        
        else:
            sendBadLoginResponse(sock, client)
            return



def sendBalance(sock, client, msg, user, df):
    row = df.loc[df['User'] == user]

    if len(row) > 0:
        msg = 'Balance: $' + str(row['Balance'].item())
    else:
        msg = 'ERR: Balance Not Found'

    sendMsg(sock, client, msg)
    updateToken(user, df)
    saveState(df)


def sendWithdraw(sock, client, msg, user, df):
    row = df.loc[df['User'] == user]

    if len(row) > 0:

        balance = row['Balance'].item()
        amount = 0
        
        try:
            amount = round(float(msg['amount']), 2)
            if amount <= 0.0 or amount > balance:
                msg = 'Withdrawal Failed, amount $' + str(amount) + ' is not able to be withdrawn from your balance of $' + str(balance)
            else:
                msg = 'Successfully withdrew $' + str(amount)
                df.loc[df['User'] == user, ['Balance']] = balance - amount
            sendMsg(sock, client, msg)
            updateToken(user, df)
            saveState(df)


        except:
            sendBadRequestResponse(sock, client, msg)
            return

        
    else:
        msg = 'ERR: User Not Found'
        sendMsg(sock, client, msg)

    

def sendDeposit(sock, client, msg, user, df):
    row = df.loc[df['User'] == user]

    if len(row) > 0:

        balance = row['Balance'].item()
        amount = 0
        
        try:
            amount = round(float(msg['amount']), 2)
            if amount <= 0.0:
                msg = 'Deposit Failed, amount $' + str(amount) + ' is not able to be deposited to your account'
            else:
                msg = 'Successfully deposited $' + str(amount)
                df.loc[df['User'] == user, ['Balance']] = balance + amount
            sendMsg(sock, client, msg)
            updateToken(user, df)
            saveState(df)


        except:
            sendBadRequestResponse(sock, client, msg)
            return

        
    else:
        msg = 'ERR: User Not Found'
        sendMsg(sock, client, msg)


def sendLogout(sock, client, user, df):

    row = df.loc[df['User'] == user]

    if len(row) > 0:
        df.loc[df['User'] == user, ['Expires']] = int(time.time())
    
    msg = 'Logged out Successfully'
    sendMsg(sock, client, msg)

    saveState(df)

def saveState(df):
    df.to_csv(PATHTOCSV, index=False)

    print('saved dataframe to disk')

def handleRequests(sock, client):

    df = pd.read_csv(PATHTOCSV)
    print(df)
    while True: 
        data = recvMsg(sock, client)
        msg = ''
        print(data)
        print(df)
        try: 
            msg = json.loads(data)
        except:
            sendBadRequestResponse(sock, client, data)
            continue

        if 'request' in msg.keys():
            request = msg['request']

            if request == 'login':
                if 'user' in msg.keys() and 'pass' in msg.keys():
                    sendLogin(sock, client, msg, df)
                    continue
                else:
                    sendBadRequestResponse(sock, client, msg)
                    continue
                    
            
            elif request == 'exit':
                sock.close()
                saveState(df)
                break
            
            else:

                if 'token' not in msg.keys():
                    sendLoginResponse(sock, client)
                    continue

                elif len(msg['token']) == 0:
                    sendLoginResponse(sock, client)
                    continue
                
                else:
                    user = getUserFromToken(msg['token'], df)

                    if not user:
                        sendBadTokenResponse(sock, client)
                        continue

                    elif request == 'balance':
                        sendBalance(sock, client, msg, user, df)
                        continue

                    elif request == 'withdrw':
                        if 'amount' in msg.keys():
                            sendWithdraw(sock, client, msg, user, df)
                            continue

                        else:
                            sendBadRequestResponse(sock, client, msg)
                            continue


                    elif request == 'deposit':
                        if 'amount' in msg.keys():
                            sendDeposit(sock, client, msg, user, df)
                            continue

                        else:
                            sendBadRequestResponse(sock, client, msg)
                            continue
                    
                    elif request == 'logout':
                        sendLogout(sock, client, user, df)
                        continue


                    else:
                        sendBadRequestResponse(sock, client, msg)
                        continue

        else:
            sendBadRequestResponse(sock, client, msg)
            continue





def sendPublicKey(sock, client, msg):
    global CLIENTPUBLICKEY
    global CLIENTN
    with client:

    # Here we should encrypt private key with the public key sent by client
        try:
            CLIENTPUBLICKEY = int(msg['public key'])
            CLIENTN = int(msg['N'])
        except:
            print('key not recieved')
            sendDefaultResponse(sock, client)
            return
        
        encryptedKey = encrypt(str(PUBLICKEY), CLIENTPUBLICKEY, CLIENTN)
        encryptedN = encrypt(str(N), CLIENTPUBLICKEY, CLIENTN)
        #print('encryptedKey', encryptedKey)
        #print('encryptedN', encryptedN)
        client.sendall(encryptedKey.encode())
        client.sendall(encryptedN.encode())
        while True: 
            
            #Grab Message
            data = client.recv(1024)
            if not data: 
                break
            
            msg = json.loads(decrypt(data.decode(), PRIVATEKEY, N))
            print('received data:', msg)

            
            if 'decrypted key' in msg.keys():

                # if decrypted key matches we know the client has a working public/private key pair

                if msg['decrypted key'] == str(PUBLICKEY):
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
        print('authenticated!')

        # Send Authenticated message so client can start making requests
        sendMsg(sock, client, 'Authenticated!')

        # Start accepting requests form the client
        handleRequests(sock, client)



#opening a listening socket on port, listening for clients to connect
if __name__ == '__main__':

    # Read in data csv file
    df = pd.read_csv(PATHTOCSV)
    print(df)

    
    PRIVATEKEY, PUBLICKEY, N = key_gen()

    print('Private key', PRIVATEKEY)
    print('Public key', PUBLICKEY)
    print('N', N)


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
                
                #parse message
                msg = json.loads(data.decode())
                
                print('received data:', msg)
                
                
                if 'public key' and 'N' in msg.keys():
                    #client.sendall('public key received'.encode())
                    sendPublicKey(s, client, msg)
                    break
                
                else:
                    print('public key not recieved')
                    sendDefaultResponse(s, client)
                    break
