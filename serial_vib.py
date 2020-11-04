import time
import serial
from sensor.CT2 import _ADS1015
PORT = '/dev/ttyUSB0'
BAUDRATE=500000

def Vib():
    global flag
    ser = serial.Serial(PORT,BAUDRATE)
    with open(f"/home/pi/Desktop/vib/{time.ctime()}.csv","w") as f:    
        while flag.value:
            while ser.in_waiting:
                data = ser.readline().decode()
                f.write(f"{data}")
    ser.close()

from multiprocessing import Process, Value
def main():
    global flag
    flag = Value('i',0)
    ads1015 = _ADS1015()
    thr = -99 #30
    count = 0
    while True:
        cur = ads1015.read()
        if cur>thr:count+=1
        else:count=0
        if count>10:
            count = 0
            print("IN")
            flag.value = 1
            p = Process(target=Vib)
            p.start()
            s = time.perf_counter()
            s2 = time.perf_counter()
            with open(f"/home/pi/Desktop/cur/{time.ctime()}.csv","w") as f:
                while time.perf_counter()-s2<6:
                #while True:
                    while time.perf_counter()-s<(1/(600+50)):pass
                    cur = ads1015.read()
                    s = time.perf_counter()
                    if cur<=thr:break
                    #print("@@@@")
                    f.write(f"{cur}\n")
                s2 = time.perf_counter()
            flag.value = 0
            p.join()
            print("OUT")
if __name__ == "__main__":
    main()