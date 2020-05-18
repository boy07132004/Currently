import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import busio
import board
class ADS1115():
    def __init__(self,pin=0,rate = 860):
        self.i2c = busio.I2C(board.SCL,board.SDA)
        self.ads = ADS.ADS1115(self.i2c)
        self.ads.data_rate = rate
        self.pin = {0:ADS.P0,1:ADS.P1,2:ADS.P2,3:ADS.P3}[pin]
    def read(self):
        return AnalogIn(self.ads,self.pin).value