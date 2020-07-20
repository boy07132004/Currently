"""   RPI | MPU9250
17 -> VCC
19 -> SDA/SDI    20 -> GND
21 -> ADO/SDO
23 -> SCLK       24 -> NCS
"""
import spidev
import time
class MPU9250_spi():
    def __init__(self,scale=2):
        self.MAX_READING=65536
        self.data_output_dir = None
        self.spi = spidev.SpiDev()   
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 976500  
        self.spi.mode = 3
        self.spi.cshigh = False
        self.mpu9250FullScaleRange = scale
        self.set_Scale()
        self.read_Init()
        print("MPU9250_SPI ready")
        
    def set_Scale(self):
        self.scale = {"2G":0x00,"4G":0x08,"8G":0x10,"16G":0x18}
        self.scale_2G = 0x00    #16384
        self.scale_4G = 0x08    #8192
        self.scale_8G = 0x10    #4096
        self.scale_16G = 0x18   #2048
        
        if(self.mpu9250FullScaleRange == 2):   
            self.Lconf = [28, self.scale['2G']]
            self.spi.xfer(self.Lconf)  #  write 16
            print('Setting Full scale range = 2G.')
    
        elif(self.mpu9250FullScaleRange == 4):
            self.Lconf = [28, self.scale['4G']]   # scale_4G = 0x08    #8192   
            self.spi.xfer(self.Lconf)  #  write 16
            print('Setting Full scale range = 4G.')
            
        elif(self.mpu9250FullScaleRange == 8):
            self.Lconf = [28,self.scale['8G']]  # scale_8G = 0x10    #4096   
            self.spi.xfer(self.Lconf)  #  write 16
            print('Setting Full scale range = 8G.')
            
        elif(self.mpu9250FullScaleRange == 16):
            self.Lconf = [28, self.scale['16G']]   # scale_2G = 0x18    #2048 
            self.spi.xfer(self.Lconf)  #  write address 28 and scale_16G 
            print('Setting Full scale range = 16G.')
        
        self.Lconf = [156, 129] #28, 1ch
        self.spi.xfer(self.Lconf)  #  write 16
        
        self.settingFullScaleRange = self.Lconf[1] & 0x18
        if ( self.settingFullScaleRange == self.scale['2G']) :
            self.scaleG = 16384
        elif ( self.settingFullScaleRange == self.scale['4G']) :
            self.scaleG = 8192
        elif ( self.settingFullScaleRange == self.scale['8G']) :
            self.scaleG = 4096
        elif ( self.settingFullScaleRange == self.scale['16G']) :
            self.scaleG = 2048
        print('Check scale = ', 32//(self.scaleG//1000))
    
    def read_(self):
        self.Lx = [187,188,129]
        self.Ly = [189,190,129]
        self.Lz = [191,192,129]        
            
        self.spi.xfer(self.Lx)            
        self.spi.xfer(self.Ly)           
        self.spi.xfer(self.Lz)      
       
        self.xAccel = (self.Lx[1]<<8)+self.Lx[2]
        self.yAccel = (self.Ly[1]<<8)+self.Ly[2]
        self.zAccel = (self.Lz[1]<<8)+self.Lz[2]
    
    def read_Init(self):
        self.start = time.perf_counter()
        print("Read init...")
        while (time.perf_counter()-self.start)<5:
            self.read_()
            time.sleep(0.001)
    
    def read(self):
        self.read_()
        if ( self.xAccel > (self.MAX_READING /2) ) :
            self.xAccel = (self.xAccel - self.MAX_READING) / self.scaleG
        else :
            self.xAccel = self.xAccel / self.scaleG
            
        if ( self.yAccel > (self.MAX_READING /2) ) :
            self.yAccel = ( self.yAccel - self.MAX_READING) / self.scaleG
        else :
            self.yAccel = self.yAccel / self.scaleG
            
        if ( self.zAccel > (self.MAX_READING /2) ) :
            self.zAccel = (self.zAccel - self.MAX_READING) / self.scaleG
        else :
            self.zAccel = self.zAccel / self.scaleG
        return self.xAccel,self.yAccel,self.zAccel
        
if __name__ == '__main__':
    mpu = MPU9250_spi()
    import pandas as pd
    start = time.perf_counter()
    ret = []
    last = start
    freq = 1000
    while time.perf_counter()-start<5:
        if time.perf_counter()-last>(1/freq)-0.00002:
            last = time.perf_counter()
            ret.append(mpu.read())
    pd.DataFrame(ret).to_csv("spi_test.csv",index=False)