import xows
import asyncio
from dotenv import load_dotenv
import os
import json

def append_to_log(ce_host, logPath, output, command):
    """This function is primarily used to append the output to the log file"""
    filename = f"{logPath}\\{ce_host}_{command}.json"
    for o in output:
        if os.path.exists(filename):
            with open(filename, 'a', encoding='utf-8') as fn:
                json.dump(o, fn)
                fn.write('\n')
        else:
            with open(filename, 'w', encoding='utf-8') as fn:
                json.dump(o, fn)
                fn.write('\n')

async def start():
    load_dotenv()
    ce_host = os.getenv('CE_HOST')
    ce_user = os.getenv('CE_USER')
    ce_pass = os.getenv('CE_PASS')
    log_path = os.getenv('LOG_PATH')

    async with xows.XoWSClient(ce_host,username=ce_user, password=ce_pass) as client:
            async def callback(data, id_):
                if id_ == 1:
                    print("new call was made")
                    print("=============================")
                    print("getting latest call")
                    call_history = await client.xCommand(['CallHistory','Get'], Limit=1, detaillevel='full')
                    call_history = call_history['Entry']
                    call_history.reverse()
                    # print(await client.xCommand(['CallHistory','Get'], Limit=1))
                    append_to_log(ce_host, log_path, call_history, 'CallHistory')
                elif id_ == 2:
                    print("Status was changed")
                    print("=============================")
                    print("getting latest status")
                    xstatus = await client.xGet(['Status'])
                    append_to_log(ce_host, log_path, xstatus, 'xStatus') 


                print(f'Feedback(Id {id_}): {data}')

            print('Subscription volume:')
            volume_id = await client.subscribe(['Status', 'Audio', 'Volume'], callback, True)

            print("Subscription callHistory Event:")
            callHistory_id = await client.subscribe(['Event', 'CallHistory'], callback, True)

            print("Subscription Status Event:")
            xstatus_id = await client.subscribe(['Status'], callback, True)

            # print("Subscription Configuration")
            # configuration_id = await client.subscribe(['Configuration'], callback, True)
            await client.wait_until_closed()

try:
    asyncio.run(start())
except KeyboardInterrupt:
    print("Keyboard interrupt; exiting...")