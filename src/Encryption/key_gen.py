
import random


f = open("src/Encryption/primes.txt","r")
large_primes = f.read().split(' ')

#given two numbers n and m returns values gcd, a, and b
#such that gcd = 1 or gcd = 0 if no modular inverse found
#and a and b are either 0 or such that a*n + b*m = gcd(n,m)
def extended_euclid(n,m):
    if n == 0:
        return m,0,1
    
    gcd, a1, b1 = extended_euclid(m%n, n)
    if gcd == 1:
        a = b1 - (m//n) * a1
        b = a1
        return gcd, a, b
    else:
        return 0,0,0
        


def key_gen():
    #generate p and q randomly
    p = int(large_primes[random.randint(0,999999)])
    while True:
        q = int(large_primes[random.randint(0,999999)])
        if q != p:
            break
    N = p*q 
    r = (p-1)*(q-1)
    e = 37633 #since 37633 is prime and our p and q values are much larger it is both 1<e<r and gcd(e,r)
    temp = extended_euclid(e,r) #d is found by running extended euclid on e and r values since d = a where a*n + b*m = gcd(n,m)
    d = temp[1] 

    return d, e, N #private key, public key, N

