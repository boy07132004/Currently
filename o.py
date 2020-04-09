from test import Curr
import time
curr = Curr(3)
#count = 0
while 1:
    #count+=1
    time_1 = time.perf_counter()
    val = (curr.read2())
    time_2 = time.perf_counter()
    print(f'{val} - {1/(time_2-time_1):.1f} Hz-{time.strftime("%H-%M-%S")}')
    time.sleep(0.5)
print(time.strftime("%H-%M-%S"))
