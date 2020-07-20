"""
RPI | MPU9250
17 -> VCC
19 -> SDA/SDI
21 -> ADO/SDO
23 -> SCLK
24 -> NCS
25 -> GND
"""
######### spidev ###################
import spidev
import time
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt


maxLogCount = 40000
nRecSeconds = 60
mpu9250FullScaleRange = 2
eqp_name = 'ABIEX100'
ch1_name = 'RR'
data_output_dir = '/home/pi/LOG_DATA'
nSleepTime = 10
nLoopCountMax = -1


scale_2G = 0x00    #16384
scale_4G = 0x08    #8192
scale_8G = 0x10    #4096
scale_16G = 0x18   #2048


def acc_xyz():
   
    MAX_READING=65536
        
    acc_x_list=[]
    acc_y_list=[]
    acc_z_list=[]    
    time_list= []
    nReadCount = 0
    time1=time.ctime()
    time1n=time.time()
    
    spi = spidev.SpiDev()   
    spi.open(0, 0)    
    spi.max_speed_hz = 976500      
    spi.mode = 3    # 2 :+1 2G 4096:1G, 
    spi.cshigh = False

    
    if(mpu9250FullScaleRange == 2):   
        Lconf = [28, scale_2G]  # scale_2G = 0x00    #16384
        spi.xfer(Lconf)  #  write 16
        print('Setting Full scale range = 2G.')
    
    elif(mpu9250FullScaleRange == 4):
        Lconf = [28, scale_4G]   # scale_4G = 0x08    #8192   
        spi.xfer(Lconf)  #  write 16
        print('Setting Full scale range = 4G.')
        
    elif(mpu9250FullScaleRange == 8):
        Lconf = [28, scale_8G]  # scale_8G = 0x10    #4096   
        spi.xfer(Lconf)  #  write 16
        print('Setting Full scale range = 8G.')
        
    elif(mpu9250FullScaleRange == 16):
        Lconf = [28, scale_16G]   # scale_2G = 0x18    #2048 
        spi.xfer(Lconf)  #  write address 28 and scale_16G 
        print('Setting Full scale range = 16G.')

    Lconf = [156, 129] #28, 1ch
    spi.xfer(Lconf)  #  write 16   
    settingFullScaleRange = Lconf[1] & 0x18
    #print('read = ', Lconf)
    if ( settingFullScaleRange == scale_2G) :
        scaleG = 16384
    elif ( settingFullScaleRange == scale_4G) :
        scaleG = 8192
    elif ( settingFullScaleRange == scale_8G) :
        scaleG = 4096
    elif ( settingFullScaleRange == scale_16G) :
        scaleG = 2048
    print('Check scale = ', scaleG)    
    nCount= 0
    
    
    time1=time.ctime()
    time1n=time.time()
    while ( (time.time() - time1n) < 15) :
        Lx = [187,188,129]
        Ly = [189,190,129]
        Lz = [191,192,129]        
            
        spi.xfer(Lx)            
        spi.xfer(Ly)           
        spi.xfer(Lz)      
       
        xAccel = (Lx[1]<<8)+Lx[2]
        yAccel = (Ly[1]<<8)+Ly[2]
        zAccel = (Lz[1]<<8)+Lz[2]  
        nCount = nCount +1
        time.sleep(0.00001)
   
    print('Start MPU9250 logging ....', nCount)
    time1=time.ctime()
    time1n=time.time()
    prevTime = time.time()
    derex=0 
    while True:
        
        if (( time.time() - prevTime ) > 0.00024) :   #0.0002 : 4641,, 0.00023:4263, 0.00024:4098
            prevTime = time.time()
            nReadCount = nReadCount + 1          
               
            Lx = [187,188,129]
            Ly = [189,190,129]
            Lz = [191,192,129]        
            
            spi.xfer(Lx)            
            spi.xfer(Ly)           
            spi.xfer(Lz)      
           
            xAccel = (Lx[1]<<8)+Lx[2]
            yAccel = (Ly[1]<<8)+Ly[2]
            zAccel = (Lz[1]<<8)+Lz[2]
      
                   
            if ( xAccel > (MAX_READING /2) ) :
                xAccel = (xAccel - MAX_READING) / scaleG
            else :
                xAccel = xAccel / scaleG
                
            if ( yAccel > (MAX_READING /2) ) :
                yAccel = ( yAccel - MAX_READING) / scaleG
            else :
                yAccel = yAccel / scaleG
                
            if ( zAccel > (MAX_READING /2) ) :
                zAccel = (zAccel - MAX_READING) / scaleG
            else :
                zAccel = zAccel / scaleG
            
            acc_x_list.append(xAccel)
            acc_y_list.append(yAccel)
            acc_z_list.append(zAccel)
            time_list.append(time.ctime())     
            
          
            #print("xAccel {:.4f}, yAccel {:.4f}, zAccel {:.4f}\n".format(xAccel,yAccel,zAccel))  
            
            #time.sleep(0.1)
            
            
            if (nReadCount > maxLogCount) :
                sf= int(maxLogCount // (time.time() - time1n))
                print(time1,time.ctime(), time.time() - time1n, 'sf=',sf )
                #print(time1,time.ctime(), time.time() - time1n)
                #sf= int(maxLogCount // (time.time() - time1n))
                #print("sf=", sf)
                
                #plt.figure(figsize=(18,6))
                #plt.plot(acc_x_list)
                #plt.plot(acc_y_list)
                #plt.plot(acc_z_list)
                #plt.show()
                
                result= pd.DataFrame(time_list, columns=['Time'])
               
                result['aX'] = acc_x_list
                result['ay'] = acc_y_list
                result['aZ'] = acc_z_list
                if not ( os.path.isdir(data_output_dir)) :
                    os.mkdir(data_output_dir)
                outFilename="./{}/{}_{}".format(data_output_dir, eqp_name,ch1_name) + time.strftime("_%Y%m%d_%H%M%S", time.localtime())+ "_{}.csv".format(sf) 
                result.to_csv(outFilename, index=False)               
                derex=derex+1
                if derex > 1:
                    sys.exit(0)          
                
                nReadCount = 0
                acc_x_list=[]
                acc_y_list=[]
                acc_z_list=[]
                time_list =[]
                
                time1=time.ctime() 
                time1n=time.time()
                if ( nLoopCountMax > 0 ) :
                    if ( nLoopCount >= nLoopCountMax) :  ##30
                        #A0_list=[]
                        time.sleep(nSleepTime)
                        nLoopCount = 0
                        time1 = time.ctime()
                        time1n=time.time() 
        
        
        
        
acc_xyz()
