import asyncio
import aiohttp
import csv
import time
from rich.progress import track
import argparse


async def data_reader(input_file: str, data_queue: asyncio.Queue):
    with open(input_file, newline='') as file:
        
        #Read every csv line as a dictionnary, with the first line as keys
        #Store the data in an asyncio.Queue object
        reader = csv.DictReader(file, delimiter=',')
        for row in reader:
            await data_queue.put(row)

async def post_url(url: str, session: aiohttp.ClientSession, payload: dict):
    async with session.post(url, json=payload) as resp:
        if resp.status != 200:
            print(f'[x] Error {resp.status} on payload {payload}')
        return await resp.text()


async def inject(r, input_file, url):
    
    #Generate the stack of data
    q = asyncio.Queue()
    await data_reader(input_file, q)

    tasks = []

    #Limit the number of concurrent connections, whether with a semaphore or through the transport layer
    # sem = asyncio.Semaphore(100)
    conn = aiohttp.TCPConnector(limit=r)

    #Create one client session that will rule them all
    async with aiohttp.ClientSession(connector=conn) as session:
    
        #Create as many tasks as there are lines of data to inject
        for i in track(range(q.qsize()), description="Building the requests..."):
        
            #Get the data to inject from the Queue object
            payload = await q.get()

            #Pass the url, session object and data dict to each request
            task = asyncio.ensure_future(post_url(url, session, payload))
            tasks.append(task)
    
        print(f'We have {len(tasks)} requests in the pipe.')

        #Track the completion of requests through an "as_completed"
        for t in track(asyncio.as_completed(tasks), total=len(tasks), description="Running the requests..."):
            response = await t
            



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-r","--requests", dest='requests', help="Specify the max number of concurrent requests you want", required=True, type=int)
    parser.add_argument("-i","--input", dest='input', help="Input file in csv format", required=True, type=str)
    parser.add_argument("-o","--output", dest='output', help="Destination of data flow as a URL", required=True, type=str)
    args = parser.parse_args()

    start = time.perf_counter()

    asyncio.run(inject(args.requests, args.input, args.output))
    end = time.perf_counter()
    print(f'Performance: {end-start} secs.')
    

if __name__=="__main__":
    main() 