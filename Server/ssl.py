import socket
import json
import random
import pandas as pd
from secrets import token_hex
import time


HOST = '127.0.0.1' 
PORT = 1024


# THIS KEY IS A PLACEHOLDER, IT SHOULD BE REPLACED WHEN WE INTEGRATE ENCRYPTION

PRIVATEKEY = '987654321'

PATHTOCSV = 'Server/Data/data.csv'


def sendDefaultResponse(sock, client):
    print('authentication failed')
    client.sendall('ERR: AUTHENTICATION FAILED'.encode())
    sock.close()

def sendBadRequestResponse(sock, client, message):
    print('Bad Request received from client', message)
    client.send('ERR: BAD REQUEST, TYPE HELP FOR LIST OF COMMANDS AND USAGE'.encode())
    handleRequests(sock, client)

def sendLoginResponse(sock, client):
    print('Bad Request received, client is not logged in')
    client.send('ERR: YOU ARE NOT LOGGED IN, PLEASE LOG IN TO MAKE REQUESTS TO THE SERVER'.encode())
    handleRequests(sock, client)

def sendBadLoginResponse(sock, client):
    print('Bad Login received')
    client.send('null'.encode())
    client.send('ERR: BAD LOGIN, THAT COMBINATION OF USER AND PASSWORD IS NOT FOUND IN OUR DATABASE'.encode())
    handleRequests(sock, client)

def sendBadTokenResponse(sock, client):
    print('Bad Token received')
    client.send('ERR: BAD/EXPIRED TOKEN, PLEASE LOG IN AGAIN'.encode())
    handleRequests(sock, client)


def sendMsg(sock, client, msg):

    # encrypt message with clients public key
    client.send(msg.encode())
    print('sent message to client')
    #handleRequests(sock, client)

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


def sendLogin(sock, client, msg, df):
   
    user = msg['user']
    passw = msg['pass']

    row = df.loc[df['User'] == user]
    
    if len(row) < 1:
        sendBadLoginResponse(sock, client)
        return
    
    else:
        if row['Pass'].item() == passw:

            newToken = token_hex(64)
            df.loc[df['User'] == user, ['Token']] = newToken
            df.loc[df['User'] == user, ['Expires']] = int(time.time()) + 900
            sendMsg(sock, client, newToken)
            sendMsg(sock, client, 'Welcome back ' + user + '!')
            saveState(df)
        
        else:
            sendBadLoginResponse(sock, client)
            return

    handleRequests(sock, client)

def sendBalance(sock, client, msg, user, df):
    row = df.loc[df['User'] == user]

    if len(row) > 0:
        msg = 'Balance: $' + str(row['Balance'].item())
    else:
        msg = 'ERR: Balance Not Found'

    sendMsg(sock, client, msg)
    handleRequests(sock, client)

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
            saveState(df)


        except:
            sendBadRequestResponse(sock, client, msg)
            return

        
    else:
        msg = 'ERR: User Not Found'
        sendMsg(sock, client, msg)

    handleRequests(sock, client)
    

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
            saveState(df)


        except:
            sendBadRequestResponse(sock, client, msg)
            return

        
    else:
        msg = 'ERR: User Not Found'
        sendMsg(sock, client, msg)

    handleRequests(sock, client)

def sendLogout(sock, client, user, df):

    row = df.loc[df['User'] == user]

    if len(row) > 0:
        df.loc[df['User'] == user, ['Expires']] = int(time.time())
    
    msg = 'Logged out Successfully'
    sendMsg(sock, client, msg)

    saveState(df)
    handleRequests(sock, client)

def saveState(df):
    df.to_csv(PATHTOCSV, index=False)

    print('saved dataframe to disk')

def handleRequests(sock, client):

    df = pd.read_csv(PATHTOCSV)
    print(df)
    data = None
    while not data: 
        data = client.recv(1024)
    msg = ''
    print(data.decode())
    try: 
        msg = json.loads(data.decode())
    except:
        sendBadRequestResponse(sock, client, data.decode())

    if 'request' in msg.keys():
        request = msg['request']

        if request == 'login':
            if 'user' in msg.keys() and 'pass' in msg.keys():
                sendLogin(sock, client, msg, df)
            else:
                sendBadRequestResponse(sock, client, msg)
                
        
        elif request == 'exit':
            sock.close()
            saveState(df)
            return
        
        else:

            if 'token' not in msg.keys():
                sendLoginResponse(sock, client)

            elif len(msg['token']) == 0:
                sendLoginResponse(sock, client)
            
            else:
                user = getUserFromToken(msg['token'], df)

                if not user:
                    sendBadTokenResponse(sock, client)

                elif request == 'balance':
                    sendBalance(sock, client, msg, user, df)

                elif request == 'withdraw':
                    if 'amount' in msg.keys():
                        sendWithdraw(sock, client, msg, user, df)

                    else:
                        sendBadRequestResponse(sock, client, msg)


                elif request == 'deposit':
                    if 'amount' in msg.keys():
                        sendDeposit(sock, client, msg, user, df)

                    else:
                        sendBadRequestResponse(sock, client, msg)
                
                elif request == 'logout':
                    sendLogout(sock, client, user, df)


                else:
                    sendBadRequestResponse(sock, client, msg)

    else:
        sendBadRequestResponse(sock, client, msg)





def sendPrivateKey(sock, client):
    with client:

    # Here we should encrypt private key with the public key sent by client

        client.sendall(PRIVATEKEY.encode())
        while True: 
            
            #Grab Message
            data = client.recv(1024)
            if not data: 
                break
            
            msg = json.loads(data.decode())
            print('received data:', msg)

            
            if 'decrypted key' in msg.keys():

                # if decrypted key matches we know the client has a working public/private key pair

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
        print('authenticated!')

        # Send Authenticated message so client can start making requests
        client.sendall('Authenticated!'.encode())

        # Start accepting requests form the client
        handleRequests(sock, client)



#opening a listening socket on port, listening for clients to connect
if __name__ == '__main__':

    # Read in data csv file
    df = pd.read_csv(PATHTOCSV)
    print(df)


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
                
                
                if 'public key' in msg.keys():
                    #client.sendall('public key received'.encode())
                    sendPrivateKey(s, client)
                    break
                
                else:
                    print('public key not recieved')
                    sendDefaultResponse(s, client)
                    break
