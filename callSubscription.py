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
            async def callback(data, id_):
                if id_ == 1:
                    print("new call was made")
                    print("=============================")
                    print("getting latest call")
                    print(await client.xCommand(['CallHistory','Get'], Limit=1))

                print(f'Feedback(Id {id_}): {data}')

            print('Subscription volume:')
            volume_id = await client.subscribe(['Status', 'Audio', 'Volume'], callback, True)

            print("Subscription callHistory Event:")
            callHistory_id = await client.subscribe(['Event', 'CallHistory'], callback, True)

            # print("Subscription Configuration")
            # configuration_id = await client.subscribe(['Configuration'], callback, True)
            await client.wait_until_closed()

try:
    asyncio.run(start())
except KeyboardInterrupt:
    print("Keyboard interrupt; exiting...")