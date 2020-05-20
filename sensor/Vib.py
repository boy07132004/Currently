from smbus2 import SMBus
class MPU9250():
    def __init__(self,bus=1):
        self.power_mgmt_1 = 0x6b
        #self.power_mgmt_2 = 0x6c
        self.bus = SMBus(bus)      # or bus = SMBus(1) for Revision 2 boards
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

if __name__ == '__main__':
    mpu = MPU9250()
    import time
    while 1:
        print(mpu.read())
        time.sleep(0.2)