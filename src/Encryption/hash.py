import struct
import io

#given message m rotate it by bits b
def rotate(m, b):
    return ((m << b) | (m >> (32 - b))) & 0xFFFFFFFF

#given new chunk of size 64 and digest h perform the operations and 
#return the updated digest h
def chunk_m(chunk, h):
    w = [0]
    while len(w) < 80:
        w.append(0)
    for i in range(16):
        w[i] = struct.unpack(b'>I', chunk[i * 4:i * 4 + 4])[0]
    for i in range(16,80):
        w[i] = rotate((w[i-3] ^ w[i-8] ^ w[i-14] ^ w[i-16]), 1)
    a, b, c, d, e = h[0], h[1], h[2], h[3], h[4]
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
    
    h[0] = (h[0] + a) & 0xFFFFFFFF
    h[1] = (h[1] + b) & 0xFFFFFFFF
    h[2] = (h[2] + c) & 0xFFFFFFFF
    h[3] = (h[3] + d) & 0xFFFFFFFF
    h[4] = (h[4] + e) & 0xFFFFFFFF
    return h

#takes in as input a bytes object message m 
#pads m to 512 bits and breaks the padded message into chunks
#using chunk_m() so each chunk is used to update the digest
#then if there is any remaining message (that isn't congruent to 448 mod 512)
#append onto it and update the digest one final time
#returns the hash in hex format
def sha1(m):
    #define initial list of hex numbers for digest
    h = [0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0]
    msg_len = 0 #length in bytes
    #pad to 512 bits
    if len(m) < 64:
        m = m.ljust(64,b'0')
    #use BytesIO to read message from bytes object m
    m = io.BytesIO(m)
    chunk = m.read(64)
    while len(chunk) == 64:
        h = chunk_m(chunk,h)
        msg_len += 64
        chunk = m.read(64)
    # return ''.join('%08x'%i for i in h)

    #once its done reading all 64 byte chunks any remaining bytes will now be used
    extra = m.read()
    extra += b'\x80'
    extra += b'\x00' * ((448 - ((msg_len*8) + 8)) % 512)
    extra += struct.pack(b'>Q', msg_len*8)
    
    h = chunk_m(extra[:64], h)
    if len(extra) == 64:
        return ''.join('%08x'%i for i in h)
    return ''.join('%08x'%i for i in chunk_m(extra[:64], h))



