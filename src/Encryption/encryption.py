#given a message m, using public key e and N
def encrypt(m, e, N):
    msg = [ord(c) for c in m]
    cphr = []
    for i in msg:
        x = (int(i)**e) % N
        cphr.append(x)
    return cphr

def decrypt(m, d, N):
    pln = []
    for i in m:
        x = (int(i)**d) % N
        pln.append(chr(x))

    return ''.join(pln)