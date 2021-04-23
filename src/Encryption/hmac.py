import hash

#input key k and message m
def hmac(k,m):
    bin_m = ''.join(format(ord(i), '08b') for i in str(m))
    block_size = 64 
    opad = b'01011100' * 8 # 0x5C
    ipad = b'00110110' * 8 # 0x36
    
    #if key is longer than the block size hash it to a fixed length
    if len(k) > block_size:
        k = hash.sha1(k)

    #if key is shorter than the block size pad it to the block size
    if len(k) < block_size:
        k = k.ljust(block_size, b'0')

    opad_k = bin(int(k,2) ^ int(opad,2))
    ipad_k = bin(int(k,2) ^ int(ipad,2))

    #formatting here is concatenating the binary strings of the padded keys with the existing message binary string bin_m 
    #the output of the sha1 function is a hex so there is extra formatting here to turn it back to binary before concatenating the binary strings after the first sha1 call
    return hash.sha1((opad_k[2:] + bin(int(hash.sha1((ipad_k[2:] + bin_m).encode()),16))[2:] ).encode()) 


