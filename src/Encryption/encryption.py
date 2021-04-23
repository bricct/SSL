
import random

#given a message m, using public key e and N return the encrypted ciphertext
#first element of list is the length of the message so we know how long it is
#then at the end of encryption we append a random number of other values
def encrypt(m, e, N):
    mlen = [len(m)]
    msg = [ord(c) for c in m]
    mlen += msg
    cphr = []
    #add random number of random numbers
    num_rands = random.randint(1,16)
    for i in range(num_rands):
        mlen.append( random.randint(1,120))
    #encrypt everything
    for i in mlen:
        x = pow(int(i),e, N)
        cphr.append(str(x))
    
    return '||'.join(cphr)

#given a message m, using the private key d and N return the decrypted plaintext
def decrypt(m, d, N):
    msg = m.split('||')
    mlen = pow(int(msg[0]),d,N) #first value is length of message
    pln = []
    for i in msg[1:mlen+1]: #iterate over only the message and ignore the random numbers at the end
        x = pow(int(i),d, N)
        pln.append(chr(x))
    return ''.join(pln)

