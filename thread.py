import threading 
import time 
from concurrent.futures import ThreadPoolExecutor

def sq(num):
   
    print(f"Square : {num*num}")
    

def cube(num):
    
    print(f"Cube : {num*num*num}")
    


# t1 = threading.Thread(target=sq,args=(4,))
# t2 = threading.Thread(target=cube,args=(4,))

# t1.start()
# t2.start()

with ThreadPoolExecutor(max_workers=2) as f:
    f.submit(sq,2)
    f.submit(cube,3)




