from sensor.Vib_SPI import MPU9250
from sensor.CT import ADS1015

def StartVib(sensor_1,sensor_2,q):
    try:
        time_last = time.perf_counter()
        ans = ""
        while sensor_1.value>-999:
            time_now  = time.perf_counter()
            if ( time_now - time_last ) > 0.00099:
                ans+=(str(round(1/(time_now-time_last),0))+','+str(sensor_2.read())[1:-1].replace(" ","")+','+str(sensor_1.value)+'\n')
                #ans.append([time_now]+list(sensor_2.read())+[sensor_1.value])
                time_last = time_now
    except Exception as e:
        ans = 'ERROR'
        print(e)
    finally:
        q.put(ans[:-1])


def Reboot():
    import os
    print('Reboot in 10s...')
    global server
    server.stop()
    time.sleep(10)
    os.system('sudo reboot')



def Monitor():
    sensor_1 = ADS1015()
    sensor_2 = MPU9250()
    threshold_1 = threshold.get_value()
    count = 0
    while State.get_value()>0:
        try:
            values = sensor_1.read()
            time.sleep(0.1)
            if count>100:
                print(f'Curr now : {values}')
                count = 0
                State.set_value(State.get_value()-1)
            if values>=threshold_1:
                print('Machine On')
                ct_Value = Value('f',values)
                q = Queue()
                p = Process( target=StartVib , args=(ct_Value,sensor_2,q))
                p.start()
                print(ct_Value.value)
                s = time.time()
                buf = 0
                while True:
                    ct_Value.value = sensor_1.read()
                    if ct_Value.value>=threshold_1:
                        buf = 0
                        if time.time()-s>300:
                            ct_Value.value=-1000
                            break
                    elif buf<60:
                        buf+=1
                    else:
                        ct_Value.value=-1000
                        break
                ans = q.get()
                p.join()
                if ans=='ERROR':
                    Reboot()
                elif len(ans)>3000*20: # Set value
                    Data_List.set_value(ans)
                    print(f'Data collected...')
            count+=1
        except Exception as e:
            print('Error - Monitor()')
            print(e)
            Reboot()


if __name__ == '__main__':
    import time
    from opcua import ua, Server
    from multiprocessing import Process, Value, Queue
    print('Running.....')
    server = Server()
    server.set_endpoint("opc.tcp://0.0.0.0:4840/")
    idx = server.register_namespace("ML6A01")
    objects = server.get_objects_node()
    myacc = objects.add_object(idx, "MyACC")
    State = myacc.add_variable(idx, "State", 0)
    State.set_writable()
    Data_List = myacc.add_variable(idx, "Data_List", [''])
    threshold = myacc.add_variable(idx, "CT_Threshold",3000)
    threshold.set_writable()
    
    server.start()
    count = 0
    #Loop start
    while True:
        try:
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
                time.sleep(1.5)
            count+=1
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(e)
