import asyncio
import aiohttp
import csv
import time
from rich.progress import track


async def data_reader(input_file: str, data_queue: asyncio.Queue):
    with open(input_file, newline='') as file:
        reader = csv.reader(file, delimiter=',')
        for row in reader:
            await data_queue.put(row)

async def post_url(url: str, session: aiohttp.ClientSession, payload: dict):
    async with session.post(url, json=payload) as resp:
        # print(f'Response status: {resp.status}')
        return await resp.text()


async def main(r, input_file):
    
    #Generate the stack of data
    q = asyncio.Queue()
    await data_reader(input_file, q)

    # base_url = "https://httpbin.org/post"     #Potential API Endpoint

    url = "http://127.0.0.1:8000"     #Potential API Endpoint
    tasks = []

    #Create instance of Semaphore to limit number of concurrent requests
    # sem = asyncio.Semaphore(100)
    conn = aiohttp.TCPConnector(limit=r)

    #Create one client session that will rule them all
    async with aiohttp.ClientSession(connector=conn) as session:
    
        #This loop injects the data with a 'r' number of simultaneous requests
        for i in track(range(q.qsize()), description="Building the requests..."):
        
            #Generate the unique url from the Queue stack. Fake code atm.
            payload = await q.get()
            ind = ['index','organization','name','website','country','description','founded','industry','employees']
            dico = dict(zip(ind, payload))
            #Pass the session to each request
            task = asyncio.ensure_future(post_url(url, session, dico))
            tasks.append(task)
    
        print(f'We have {len(tasks)} requests in the pipe.')
        # responses = asyncio.gather(*tasks)
        for t in track(asyncio.as_completed(tasks), total=len(tasks), description="Running the requests..."):
            response = await t
            
        # await responses


concurrent_requests = 100

start = time.perf_counter()
asyncio.run(main(concurrent_requests, 'organizations-100.csv'))
# asyncio.run(main(concurrent_requests, 'organizations-500000.csv'))
end = time.perf_counter()
print(f'Performance: {end-start}')

#Current ratio with 100 concurrent_requests: 5747 requests / second!!!


