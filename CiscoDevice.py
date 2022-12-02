import xows
from dotenv import load_dotenv
from Device import Device
import asyncio
import os

class CiscoDevice(Device):
    """A Class to manage the cisco device"""
    def __init__(self, name, ip_address, username, password, log_path):
        super().__init__(name, ip_address, username, password, log_path)
        self.client =  xows.XoWSClient(self.ip_address,username=self.username, password=self.password)
        self.iterator = 0

    async def connect(self):
        """Connects to the device using websockets"""
        await self.client.connect()
    
    def disconnect(self):
        """Disconnects from the device"""
        self.client.disconnect()

    async def set_call_history_subscription(self):
        """Creates a callHistory event subscription"""
        await self.client.subscribe(['Event', 'CallHistory'], self.callback, True)

    async def set_volume_subscription(self):
        """Creates a volume event subscription"""
        await self.client.subscribe(['Status', 'Audio', 'Volume'], self.callback, True)
    
    async def set_xStatus_subscription(self):
        """Creates a xstatus subscription"""
        await self.client.subscribe(['Status'], self.callback, True)
    
    def get_call_history(self, limit=1):
        """Gets the call history. 
        Takes a limit variable"""
        call_history = self.client.xCommand(['CallHistory','Get'], Limit=1, detaillevel='full')
        return call_history

    def prepare_call_history(self, call_history):
        call_history = call_history['Entry']
        call_history.reverse()
        return call_history
    
    def get_xstatus(self):
        """Gets the xstatus"""
        xstatus = self.client.xGet(['Status'])
        return xstatus

    def check_iterator(self):
        """Checks the iterator to see if it's time to run the new xstatus command"""
        if self.iterator == 0:
            self.iterator+=1
            return True
        elif self.iterator < 900:
            self.iterator+=1
            return False
        else:
            self.iterator = 1
            return True
        

    
    async def callback(self, data, id_):
        if id_ == 0:
            print("new call was made")
            print("=============================")
            print("getting latest call")
            call_history = await self.get_call_history()
            call_history = self.prepare_call_history(call_history)
            for call in call_history:
                self.append_to_log(call, "CallHistory")
        elif id_ == 2:
            print("status changed")
            if self.check_iterator():
                xstatus  = await self.get_xstatus()
                self.append_to_log(xstatus, "xstatus")


        
        print(f'Feedback(Id {id_}): {data}')

async def main():
    load_dotenv()
    name = "device1"
    ip_address = os.getenv('CE_HOST')
    username = os.getenv('CE_USER')
    password = os.getenv('CE_PASS')
    log_path = os.getenv('LOG_PATH')
    dev1 = CiscoDevice(name=name, ip_address=ip_address, username=username, password=password, log_path=log_path)
    await dev1.connect()
    await dev1.set_call_history_subscription()
    await dev1.set_volume_subscription()
    await dev1.set_xStatus_subscription()
    await dev1.client.wait_until_closed()

if __name__ == "__main__":
    asyncio.run(main())