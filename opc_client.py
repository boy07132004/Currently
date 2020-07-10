import sys
import time
import asyncio
from asyncua import Client
from pandas import DataFrame

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
            DataFrame(val[1:]).to_csv(f"C:\\csv_log2\\{time_now}.csv",index=False,header=False)

async def main():
    global running
    try:
        async with Client(url="opc.tcp://192.168.0.100:4840/") as client:
            announcement('Connected')
            state = client.get_node("ns=2;i=2")
            data_list = client.get_node("ns=2;i=3")
            await client.get_node("ns=2;i=4").set_value(300) # Threshold
        # Check data change
            handler = SubHandler()
            sub = await client.create_subscription(500, handler)
            handle = await sub.subscribe_data_change(data_list)
            while True:
                try:
                    await state.write_value(3)
                    await asyncio.sleep(10)
                except Exception as e:
                    print(e)
                    break
    finally:
        if running:
            announcement('Disconnected')
        else:
            await state.set_value(0)
        announcement('End')

if __name__ == "__main__":
    running = True
    while running:
        try:
            asyncio.run(main())
        except Exception as e:
            print(e)
        announcement('Reconnect in 30s')
        time.sleep(29)