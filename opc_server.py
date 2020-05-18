from Vib import MPU9250
from CT import ADS1115

def Start_Vib(curr,q):
    try:
        vib = MPU9250()
        time_last = 0.0
        ans = []
        while curr.value>3000:
            time_now  = time.perf_counter()
            ac_x = ac_y = ac_z = -999
            if ( time_now - time_last ) > 0.00099:
                ac_x, ac_y, ac_z = vib.read()
                ans.append([1/(time_now-time_last),ac_x,ac_y,ac_z,curr.value])
                time_last = time_now
    except:
        ans = 'ERROR'
    q.put(ans)


def reboot():
    import os
    print('Reboot in 10s...')
    global server
    server.stop()
    time.sleep(10)
    os.system('sudo reboot')


from opcua import ua, Server
from multiprocessing import Process, Value, Queue
def Monitor():
    #read_analog_values from A()
    curr = ADS1115()
    #---Variables---#
    Curr_threshold = 3000
    count = 0
#---Variables---#
    global State
    while State.get_value()>0:
        try:
            values = curr.read()
            time.sleep(0.1)
            if count>100:
                print(f'Curr now : {values}')
                count = 0
                State.set_value(State.get_value()-1)
            if values>=Curr_threshold:
                print('Machine On')
                var = Value('f',values)
                q = Queue()
                p = Process( target=Start_Vib , args=(var,q))
                p.start()
                print(var.value)
                while var.value>=Curr_threshold:
                    var.value = curr.read()
                ans = q.get()
                p.join()
                if ans=='ERROR':
                    reboot()
                elif len(ans)>1:
                    Data_List.set_value(ans)
                print(f'Data collected... Len:{len(ans)}')
                del ans
            count+=1
        except:
            print('Error - Monitor()')
            reboot()


if __name__ == '__main__':
    import time
    print('Start in 2s...')
    time.sleep(2)
    count = 0
    server = Server()
    server.set_endpoint("opc.tcp://192.168.0.111:4840/")
    idx = server.register_namespace("ML6A01")
    objects = server.get_objects_node()
    
    myacc = objects.add_object(idx, "MyACC")
    State = myacc.add_variable(idx, "State", 0)
    State.set_writable()
    Data_List = myacc.add_variable(idx, "Data_List", [''])
    
    server.start()
    running = True
    #Loop start
    while running:
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
        except:
            pass