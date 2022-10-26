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
            def callback(data, id_, ce_host):
                print(f'Host: {ce_host}\nFeedback(Id {id_}): {data}')

            print('Subscription 0:',
            await client.subscribe(['Status', 'Audio', 'Volume'], callback, True))

            print("Subscription 1:",
            await client.subscribe(['Command', 'CallHistory', 'Get'], Limit=1))

            await client.wait_until_closed()

asyncio.run(start())