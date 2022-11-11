import xows
from dotenv import load_dotenv

class CiscoDevice(Device):
    """A Class to manage the cisco device"""
    def __init__(self):
        super().__init__(self, name, ip_address, username, password, log_path)
        self.client =  xows.XoWSClient(self.ip_address,username=self.username, password=self.password)

    async def connect(self):
        """Connects to the device using websockets"""
        self.client.connect()
        await self.client.wait_until_closed()
    
    def disconnect(self):
        """Disconnects from the device"""
        self.client.disconnect()

    async def set_call_history_subscription(self, client):
        """Creates a callHistory event subscription"""
        await client.subscribe(['Event', 'CallHistory'], self.callback, True)

    async def set_volume_subscription(self):
        """Creates a volume event subscription"""
        await self.subscribe(['Status', 'Audio', 'Volume'], self.callback, True)
    
    def get_call_history(self, limit=1):
        """Gets the call history. 
        Takes a limit variable"""
        call_history = self.client.xCommand(['CallHistory','Get'], Limit=1, detaillevel='full')
        return call_history
    
    async def callback(self, data, id_):
        if id_ == 0:
            print("new call was made")
            print("=============================")
            print("getting latest call")
            call_history = self.get_call_history()
            print(call_history)
        
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
    dev1.set_call_history_subscription()
    dev1.set_volume_subscription()