#Using SHA-1 for our hash algorithm 

#given messsage m and bits b left shift m by b bits
def lshift(m, b):
    return m << b

#given message m and bits b rotate m by b bits
def rotate(m, b):
    return ((m << b) | (m >> (32 - b))) & 0xFFFFFFFF



def sha1(m):
    #define list of hex numbers that will remain constant
    hex = [0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0]

    #pad the input message m 
    


