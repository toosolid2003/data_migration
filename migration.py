import asyncio
import aiohttp
import csv
import time
import rich


async def data_reader(input_file: str, data_queue: asyncio.Queue):
    with open(input_file, newline='') as file:
        reader = csv.reader(file, delimiter=',')
        for row in reader:
            await data_queue.put(row)

async def post_url(url: str, session: aiohttp.ClientSession):
    async with session.post(url) as resp:
        # print(f'Response status: {resp.status}')
        return await resp.text()

async def bound_fetch(sem, url, session):
    #Getter function with a semaphore
    async with sem:
        await post_url(url, session)

async def main(r, input_file):
    
    #Generate the stack of data
    q = asyncio.Queue()
    await data_reader(input_file, q)

    base_url = "https://httpbin.org/post"     #Potential API Endpoint
    tasks = []

    #Create instance of Semaphore to limit number of concurrent requests
    sem = asyncio.Semaphore(100)

    #Initiate a counter of iterations, to know how many times the while loop runs.
    n = 0 
    while q.empty() == False:
        
        #If the size of the stack is less than the number of concurrent requests, we decrease the
        #number of concurrent requests to adapt to the stack size

        if q.qsize() < r:
            r = q.qsize()

        #Create one client session that will rule them all
        async with aiohttp.ClientSession() as session:
            
            #This loop injects the data with a 'r' number of simultaneous requests
            for i in range(r):
                
                #Generate the unique url from the Queue stack. Fake code atm.
                url = base_url
                payload = await q.get()
                # print(q.qsize())
                
                #Pass the semaphore and session to each request
                task = asyncio.ensure_future(bound_fetch(sem, url, session))
                tasks.append(task)
            
            responses = asyncio.gather(*tasks)
            
            await responses
            n+=1
    print(f'Number of iterations: {n}')        

concurrent_requests = 100

start = time.perf_counter()
asyncio.run(main(concurrent_requests, 'organizations-100.csv'))
end = time.perf_counter()
print(f'Performance: {end-start}')



