import RNG
import random

while True: 
    n = 16
    prime_candidate = RNG.getLowLevelPrime(n) 
    if not RNG.isMillerRabinPassed(prime_candidate): 
        continue
    else: 
 
        break

#Server's variables---------------------------
p = prime_candidate
g = random.randrange(2**(n/2-1)+1, 2**(n/2)-1)
#---------------------------------------------

#Client A's variables-------------------------
S_a = random.randrange(2**(n-1)+1, 2**(n)-1)
T_a = (g**S_a) % p
#---------------------------------------------

#Client B's variables-------------------------
S_b = random.randrange(2**(n-1)+1, 2**(n)-1)
T_b = (g**S_b) % p
#---------------------------------------------


print("p is: ", prime_candidate, '\n')
print("g is: ", g)
print("Alice's secret number: ", S_a)
print("Bob's secret number: ", S_b)
print('T_a: ' + str(T_a) + '\n')
print('T_b: ' + str(T_b) + '\n')
print("Final secret number: ", (T_a**S_b) % p)
print("Verifying: ", (T_b**S_a) % p)
