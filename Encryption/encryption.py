#given a message m, using public key e and N return the encrypted ciphertext
def encrypt(m, e, N):
    msg = [ord(c) for c in m]
    cphr = []
    for i in msg:
        x = pow(int(i),e, N)
        cphr.append(chr(x))
    return ''.join(cphr)

#given a message m, using the private key d and N return the decrypted plaintext
def decrypt(m, d, N):
    pln = []
    for i in m:
        x = pow(int(i), d, N)
        pln.append(chr(x))

    return ''.join(pln)

