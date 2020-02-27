import smbus
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
#===============================================================#
#                        MPU END
#===============================================================#
"""
import Adafruit_ADS1x15
class Curr():
    def __init__(self,pin):
        self.adc = Adafruit_ADS1x15.ADS1115()
        self.adc._data_rate_config(860)
        self.GAIN = 1
        #read_values from A(pin)
        self.ana_input = pin
    def read(self):
        #return values+1
        return self.adc.read_adc(self.ana_input, gain=self.GAIN)
"""
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
import time
from opcua import ua, Server
def Monitor():
    vib = Vib()
    #read_values from A()
    curr = Curr(3)
    #---Variables---#
    Curr_threshold = 3000
    #---Variables---#
    while State.get_value()>0:
        values = curr.read()
        time.sleep(0.1)
        print(f'Curr now : {values}')
        if values>=Curr_threshold:
            List_Per_Act = []
            time_last = 0.0
            while (values>=Curr_threshold):
                ac_x = ac_y = ac_z = 9999
                time_now = time.perf_counter()
                if (time_now-time_last)>0.001:
                    ac_x,ac_y,ac_z = vib.read()
                    List_Per_Act.append([(time_now-time_last),ac_x,ac_y,ac_z,values])
                    time_last = time_now
                values = curr.read()
            Data_List.set_value(List_Per_Act)
            del List_Per_Act

if __name__ == '__main__':
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
    server.start()
    try:
    #Loop start
        while 1:
            OPC_State = State.get_value()
            if OPC_State>0:
                Monitor()
                print('End------------------*')
            else:
                time.sleep(0.5)
            print(f'Now State : {OPC_State}')
    finally:
        server.stop()
        t = time.strftime("%H-%M-%S",time.gmtime())
        print(f'{t}-END')