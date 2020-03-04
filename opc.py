import time
time.sleep(5)
import smbus
global count
class Vib():
    def __init__(self):
        self.power_mgmt_1 = 0x6b
        self.power_mgmt_2 = 0x6c
        self.bus = smbus.SMBus(1) # or bus = smbus.SMBus(1) for Revision 2 boards
        self.address = 0x68       # This is the address value read via the i2cdetect command
        self.bus.write_byte_data(self.address, self.power_mgmt_1, 0)
    def read_word_2c(self,adr):
        self.high = self.bus.read_byte_data(self.address, adr)
        self.low = self.bus.read_byte_data(self.address, adr+1)
        self.val = (self.high << 8) + self.low
        if (self.val >= 0x8000):
            return -((65535 - self.val) + 1)
        else:
            return self.val
    def read(self):
        self.ac_x = self.read_word_2c(0x3b) / 16384.0
        self.ac_y = self.read_word_2c(0x3d) / 16384.0
        self.ac_z = self.read_word_2c(0x3f) / 16384.0

        return self.ac_x,self.ac_y,self.ac_z


def Start_Vib(curr,q):
    try:
        vib = Vib()
        time_last = 0.0
        ans = []
        while curr.value>3000:
            time_now  = time.perf_counter()
            ac_x = ac_y = ac_z = 0.1
            if ( time_now - time_last ) > 0.001:
                ac_x, ac_y, ac_z = vib.read()
                ans.append([(time_now-time_last),ac_x,ac_y,ac_z,curr.value])
                time_last = time_now
        code.put(1)
    except:
        code.put(0)
    q.put(ans)
#===============================================================#
#                        MPU END
#===============================================================#

import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import busio
import board
class Curr():
    def __init__(self,pin,rate = 860):
        self.i2c = busio.I2C(board.SCL,board.SDA)
        self.ads = ADS.ADS1115(self.i2c)
        self.ads.data_rate = rate
        self.pin = {0:ADS.P0,1:ADS.P1,2:ADS.P2,3:ADS.P3}[pin]
    def read(self):
        return AnalogIn(self.ads,self.pin).value

#===============================================================#
#                        ADS END
#===============================================================#

# Main loop

from opcua import ua, Server
from multiprocessing import Process, Value, Queue
def Monitor():
    try:
        vib = Vib()
    #read_analog_values from A()
        curr = Curr(3)
    #---Variables---#
        Curr_threshold = 3000
        count = 0
    #---Variables---#
        while State.get_value()*Ope_Code>0:
            values = curr.read()
            time.sleep(0.1)
            if count>100:
                print(f'Curr now : {values}')
                count = 0
            if values>=Curr_threshold:
                var = Value('f',values)
                code = Queue()
                q = Queue()
                p = Process( target=Start_Vib , args=(var,q,code))
                p.start()
                while var.value>=Curr_threshold:
                    var.value = curr.read()
                ans = q.get()
                Ope_Code = code.get()
                if len(ans)>1:
                    Data_List.set_value(ans)
                p.join()
            count+=1
    except:
        Ope_Code = 0
def reboot():
    import os
    time.sleep(10)
    print('Reboot in 10s...')
    os.system('sudo reboot')


if __name__ == '__main__':
    count = 0
    server = Server()
    server.set_endpoint("opc.tcp://192.168.0.101:4840/")
    uri = "ML6A01"
    idx = server.register_namespace(uri)

    # get Objects node, this is where we should put our nodes
    objects = server.get_objects_node()
    # populating our address space
    myacc = objects.add_object(idx, "MyACC")
    State = myacc.add_variable(idx, "State", 0)
    State.set_writable()
    Data_List = myacc.add_variable(idx, "Data_List", [''])
    global OPC_State
    global Ope_Code
    Ope_Code = 1
    server.start()
    try:
    #Loop start
        while Ope_Code:
            OPC_State = State.get_value()
            if count > 10:
                print(f'Now State : {OPC_State}')
                count = 0
            if OPC_State>0:
                print(f'Now State : {OPC_State}')
                print('-'*10,'Start Monitor','-'*10)
                count = 0
                Monitor()
                print('-'*10,'End Monitor','-'*10)
            else:
                time.sleep(1)
            count+=1
    except KeyboardInterrupt:
        server.stop()
        print('='*20)
        print(f'{time.ctime()}-END')
        print('='*20)
    
    reboot()

