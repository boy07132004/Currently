from adafruit_ads1x15.analog_in import AnalogIn
import busio
import board

class ADS1115():
    def __init__(self,pin=0,rate = 860):
        import adafruit_ads1x15.ads1115 as ADS
        self.i2c = busio.I2C(board.SCL,board.SDA)
        self.ads = ADS.ADS1115(self.i2c)
        self.ads.data_rate = rate
        self.pin = {0:ADS.P0,1:ADS.P1,2:ADS.P2,3:ADS.P3}[pin]
    def read(self):
        return AnalogIn(self.ads,self.pin).value

class ADS1015():
    def __init__(self,pin=0,rate = 1600):
        import adafruit_ads1x15.ads1015 as ADS
        self.i2c = busio.I2C(board.SCL,board.SDA)
        self.ads = ADS.ADS1015(self.i2c)
        self.ads.data_rate = rate
        self.pin = {0:ADS.P0,1:ADS.P1,2:ADS.P2,3:ADS.P3}[pin]
    def read(self):
        return AnalogIn(self.ads,self.pin).value
    
if __name__ == '__main__':
    import time
    ads = ADS1015(rate=2400)
    #"""
    now = time.perf_counter()
    while 1:
        print(ads.read(),1/(time.perf_counter()-now))
        now = time.perf_counter()
    """
    import csv
    with open("output.csv","w") as file:
        while 1:
            csv.writer(file).writerow([ads.read()])
    """