#!/usr/bin/env python

import xows
import asyncio
from dotenv import load_dotenv
import os

class Device:
    """A Class to manage the device"""

    def __init__(self, name, ip_address, username, password, log_path):
        """initializes the devices"""
        self.name = name
        self.ip_address = ip_address
        self.username = username
        self.password = password
        self.log_path = log_path

    def check_log_path(self):
        """Checks to make sure the logpath exists"""
        isExist = os.path.exists(self.log_path)
        if isExist == False:
            os.makedirs(self.log_path)
            
    def append_to_log(self, ce_host, logPath, output, command):
        """This function is primarily used to append the output to the log file"""
        filename = f"{logPath}{ce_host}_{command}.log"
        if os.path.exists(filename):
            with open(filename, 'a', encoding='utf-8') as fn:
                fn.write(output)
        else:
            with open(filename, 'w', encoding='utf-8') as fn:
                fn.write(output)

    async def connect(self):
        """connects to the device using websockets"""
        async with xows.XoWSClient(self.ip_address,username=self.username, password=self.password) as client:
            async def callback(data, id_):
                if id_ == 1:
                    print("new call was made")
                    print("=============================")
                    print("getting latest call")
                    call_history = await client.xCommand(['CallHistory','Get'], Limit=1, detaillevel='full')
                    call_history = call_history['Entry']
                    call_history.reverse()
                    append_to_log(ce_host, log_path, call_history, 'CallHistory')


                print(f'Feedback(Id {id_}): {data}')

            print('Subscription volume:')
            volume_id = await client.subscribe(['Status', 'Audio', 'Volume'], callback, True)

            print("Subscription callHistory Event:")
            callHistory_id = await client.subscribe(['Event', 'CallHistory'], callback, True)

            # print("Subscription Configuration")
            # configuration_id = await client.subscribe(['Configuration'], callback, True)
            await client.wait_until_closed()
    

async def main():
    load_dotenv()
    name = "device1"
    ip_address = os.getenv('CE_HOST')
    username = os.getenv('CE_USER')
    password = os.getenv('CE_PASS')
    log_path = os.getenv('LOG_PATH')
    dev1 = Device(name=name, ip_address=ip_address, username=username, password=password, log_path=log_path)
    dev1.check_log_path()
    await dev1.connect()

    


if __name__ == "__main__":
    asyncio.run(main())