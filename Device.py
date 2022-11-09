#!/usr/bin/env python

import xows
import asyncio
from dotenv import load_dotenv
import os

class Device():
    """A Class to manage the device"""
    def ___init__(self, name):
        """initializes the devices"""
        self.name = name
        load_dotenv()
        self.ip_address = os.getenv('CE_HOST')
        self.username = os.getenv('CE_USER')
        self.password = os.getenv('CE_PASS')

    def append_to_log(self, ce_host, logPath, output, command):
        """This function is primarily used to append the output to the log file"""
        filename = f"{logPath}{ce_host}_{command}.log"
        if os.path.exists(filename):
            with open(filename, 'a', encoding='utf-8') as fn:
                fn.write(output)
        else:
            with open(filename, 'w', encoding='utf-8') as fn:
                fn.write(output)
    
    def connect(self):
        """connects to the device using websockets"""
        client = xows.XoWSClient(self.ip_address,username=self.username, password=self.password)
        return client
    
    def get_call_history(self, limit=1):
        """Gets the call history. 
        Takes a limit variable"""
        call_history = client.xCommand(['CallHistory','Get'], Limit=1)
        return call_history
    
    async def set_call_history_subscription(self):
        """Creates a callHistory event subscription"""
        callHistory_id = await self.subscribe(['Event', 'CallHistory'], self.callback, True)


    async def set_volume_subscription(self):
        volume_id = await self.subscribe(['Status', 'Audio', 'Volume'], self.callback, True)

    async def callback(data, id_):
        if id == "callHistory_ID":
            print("new call was made")
            print("=============================")
            print("getting latest call")
            call_history = get_call_history()
            return call_history

async def main():
    dev1 = Device("device1")
    dev1.connect()
    dev1.set_call_history_subscription()

if __name__ == "__main__":
    main()