
#given messsage m and bits b left shift m by b bits
def lshift(m, b):
    return m << b

#given message m and bits b rotate m by b bits
def rotate(m, b):
    return ((m << b) | (m >> (32 - b))) & 0xFFFFFFFF

def pad(m):
    #store the length of the message and then append a 1 onto it
    mlen = len(m)
    m += '1'
    for i in range(512): #desired length of 512 bits when padded
        if ((len(m)+len(bin(mlen)[2:])) % 512 == 0):
            break
        m += '0'
    return m

#given a message m return a list of bytestrings (length 64)
def chunk_m(m, n):
    return [m[i:i+n] for i in range(0, len(m), n)]

def sha1(m):
    #define list of hex numbers that will remain constant
    hex = [0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0]

    #pad the input message m 
    m2 = pad(m)
    chunks = chunk_m(m2, 64)
    for chunk in chunks:
        w = list(map(lambda x: int(x,2), chunk_m(chunk, 32)))
        while len(w) < 80:
            w.append(0)
        for i in range(16,80):
            w[i] = rotate((w[i-3] ^ w[i-8] ^ w[i-14] ^ w[i-16]), 1)
        a, b, c, d, e = hex[0], hex[1], hex[2], hex[3], hex[4]

        for i in range(0,80):
            if 0 <= i < 20:
                f = (b & c) | ((~b) & d)
                k = 0x5A827999
            elif 20 <= i < 40:
                f = b ^ c ^ d
                k = 0x6ED9EBA1
            elif 40 <= i < 60:
                f = (b & c) | (b & d) | (c & d)
                k = 0x8F1BBCDC
            elif 60 <= i < 80:
                f = b ^ c ^ d
                k = 0xCA62C1D6
            a,b,c,d,e = rotate(a, 5) + f + e + k + w[i] & 0xFFFFFFFF, a, rotate(b, 30), c, d
    hex[0] += a
    hex[1] += b
    hex[2] += c
    hex[3] += d
    hex[4] += e

    return lshift(hex[0], 128) | lshift(hex[1], 96) | lshift(hex[2], 64) | lshift(hex[3], 32) | hex[4]





