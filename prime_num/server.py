from fastapi import FastAPI, HTTPException 
import time
import multiprocessing
import math
# Add your own imports for multiprocessing here
app = FastAPI()
def isPrime(n:int):
    if n<2:
        return False
    for i in range (2,int(math.sqrt(n))+1):
        if n%i==0:
            return False
    return True

def calculate_primes(number: int,q):
    # TODO: Implement the logic to find total primes, last prime, next prime 
    # # This function will run inside a separate process!
    primes_before = 0
    last_prime_before = None
    
    for i in range(2,number):
        if isPrime(i):
            primes_before+=1
            last_prime_before=i
            
    next_prime_after = number+1
    while True:
        if isPrime(next_prime_after):
            break
        next_prime_after+=1
    q.put((primes_before,last_prime_before,next_prime_after))
      
@app.get("/primes/{number}")
def get_prime_data(number: int):
    start_time = time.time()
    q = multiprocessing.Queue()
    p = multiprocessing.Process(target=calculate_primes,args=(number,q))
    p.start()
    p.join(timeout=10)
    # TODO: Execute calculate_primes(number) in a separate process 
    # TODO: Enforce the strictly 10‐second timeout here
    if p.is_alive():
        p.terminate()
        p.join()
        raise HTTPException(status_code=408, detail="Computation timeout")
    primes_before, last_prime_before, next_prime_after = q.get()
    time_taken = time.time() - start_time
    # Return the dictionary matching the JSON requirement
    return {
    "query_number": number, 
    "primes_before": primes_before, 
    "last_prime_before": last_prime_before, 
    "next_prime_after": next_prime_after, 
    "time_taken": round(time_taken,2)
    }