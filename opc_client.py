import sys
import time
import asyncio
from asyncua import Client
#from pandas import DataFrame

def announcement(word):
    print('='*10,time.ctime(),'='*10)
    print(word)
    print('-'*10)

class SubHandler(object):
    def datachange_notification(self, node, val, data):
        if (len(val) > 3000):
            announcement("New data change")
            time_ctime = time.ctime().split()
            time_now = time_ctime[1] + '_' + time_ctime[2] + '_' + time_ctime[3].replace(':','-')
            #DataFrame([['Time','X','Y','Z']]+val).to_csv(f"C:\\csv_log2\\{time_now}.csv",index=False,header=False)
            with open(f"C:\\csv_log2\\{time_now}.csv",'w',newline='') as csvfile:
                csvfile.write("Time,X,Y,Z,CT\n")
                csvfile.write(val)


async def main():
    global _Running
    try:
        async with Client(url="opc.tcp://192.168.0.102:4840/") as client:
            announcement('Connected')
            _State = client.get_node("ns=2;i=2")
            Vib_Data_List =await client.nodes.root.get_child(["0:Objects","2:MyACC","2:Data_List"])
            CT_Threshold = await client.nodes.root.get_child(["0:Objects","2:MyACC","2:CT_Threshold"])
            #CT_Data_List =await client.nodes.root.get_child(["0:Objects","2:MyACC","2:CT_Data_List"])
            await CT_Threshold.write_value(3200)
        # Check data change
            handler = SubHandler()
            sub = await client.create_subscription(500, handler)
            handle = await sub.subscribe_data_change(Vib_Data_List)
            while True:
                try:
                    await _State.write_value(3)
                    await asyncio.sleep(10)
                except Exception as e:
                    print(e)
                    break
    except Exception as e:
        print(e)
    finally:
        if _Running:
            announcement('Disconnected')
        else:
            await _State.set_value(0)
        announcement('End')

if __name__ == "__main__":
    _Running = True
    while _Running:
        try:
            asyncio.run(main())
        except Exception as e:
            print(e)
        announcement('Reconnect in 30s')
        time.sleep(29)