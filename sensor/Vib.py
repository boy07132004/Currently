from smbus2 import SMBus
import time
class MPU9250():
    def __init__(self,bus=1):
        self.power_mgmt_1   = 0x6b #107
        self.power_mgmt_2   = 0x6c #108
        self.sample_rate_div= 0x19 #25
        self.accel_cfg_2    = 0x1d #29
        self.bus = SMBus(bus)      # or bus = SMBus(1) for Revision 2 boards
        self.address = 0x68       # This is the address value read via the i2cdetect command
        self.bus.write_byte_data(self.address, self.power_mgmt_1,   0b00000000)
        self.bus.write_byte_data(self.address, self.power_mgmt_2,   0b00000111)
        self.bus.write_byte_data(self.address, self.accel_cfg_2 ,   0b00001000)
        self.bus.write_byte_data(self.address, self.sample_rate_div,0b00000000)
        time.sleep(0.5)
    
    def read_word_2c_(self,adr):
        self.val_list = self.bus.read_i2c_block_data(self.address, adr,6)
        self.ret = []
        for i in range(3):
            self.val =  (self.val_list[i*2] << 8) + self.val_list[i*2+1]
            self.val =  self.val if self.val<0x8000 else -((65535 - self.val) + 1)
            self.ret.append(round((self.val/16384.0),5))
        return self.ret
    
    def read(self):
        self.ac_x,self.ac_y,self.ac_z = self.read_word_2c_(0x3b)
        return self.ac_x,self.ac_y,self.ac_z

if __name__ == '__main__':
    mpu = MPU9250()
    import time,csv
    time_last = 0
    while True:
        ans = []
        time_now  = time.perf_counter()
        ac_x = ac_y = ac_z = -999
        if ( time_now - time_last ) > 0.00099:
            ac_x, ac_y, ac_z = mpu.read()
            ans = [1/(time_now-time_last),ac_x,ac_y,ac_z]
            time_last = time_now
            print(ans)
