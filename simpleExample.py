import xows
import asyncio
from dotenv import load_dotenv
import os

async def start():
    load_dotenv()
    ce_host = os.getenv('CE_HOST')
    ce_user = os.getenv('CE_USER')
    ce_pass = os.getenv('CE_PASS')

    async with xows.XoWSClient(ce_host,username=ce_user, password=ce_pass) as client:
        def callback(data, id_):
            print(f'Feedback(Id {id_}): {data}')
        
        print('Status Query:',
        await client.xQuery(['Status', '**', 'DisplayName']))

        print('Get status:',
        await client.xGet(['Status', 'Audio', 'Volume']))

        print('Get configuration:',
        await client.xGet(['Configuration', 'SIP', 'Proxy', 1, 'Address']))

        print('Command:',
        await client.xCommand(['Audio', 'Volume', 'Set'], Level=60))

        print('Configuration:',
        await client.xSet(['Configuration', 'Audio', 'DefaultVolume'], 50))

        print('Subscription 0:',
        await client.subscribe(['Status', 'Audio', 'Volume'], callback, True))

        await client.wait_until_closed()

asyncio.run(start())
