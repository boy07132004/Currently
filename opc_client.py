import sys
import time

from opcua import Client
from opcua import ua
import csv
import signal
def signal_handler(sig,frame):
    global running
    running = False
    announcement('SIG_INT')

def announcement(word):
    print('='*10,time.ctime(),'='*10)
    print(word)
    print('-'*10)
class SubHandler(object):
    def datachange_notification(self, node, val, data):
        # Record condition
        if len(val) > 3000:
            announcement("New data change")
            time_ctime = time.ctime().split()
            time_now = time_ctime[1] + '_' + time_ctime[2] + '_' + time_ctime[3].replace(':','-')
            with open(f"C:\\csv_log2\\{time_now}.csv",'w',newline="") as csvfile:
                field_name = ['freq','X','Y','Z','Curr']
                writer = csv.writer(csvfile)
                writer.writerow(field_name)
                writer.writerows(val[1:])

def main():
    client = Client("opc.tcp://192.168.0.111:4840/")
    global running
    try:
        client.connect()
        announcement('Connected')
        state = client.get_node("ns=2;i=2")
        data_list = client.get_node("ns=2;i=3")
        state.set_value(1)

    # Check data change
        handler = SubHandler()
        sub = client.create_subscription(500, handler)
        handle = sub.subscribe_data_change(data_list)
        while running:
            if client.uaclient._uasocket._thread.isAlive():
                state.set_value(3)
                time.sleep(10)
            else:
                break


    finally:
        if running:
            announcement('Disconnected')
        else:
            state.set_value(0)
        client.disconnect()
        announcement('End')

if __name__ == "__main__":
    running = True
    while running:
        try:
            main()
        except:
            pass
        announcement('Reconnect in 30s')
        time.sleep(29)
    
    
            
