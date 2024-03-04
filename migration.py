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
            payload['status_code'] = resp.status
            return payload
        
        await resp.text()
        


def error_log(errors: list):
    with open('error_log.csv','w', newline='') as csvfile:
        fields = ['status_code','error_msg','index','organization','name','website','country','description','founded','industry','employees']
        writer = csv.DictWriter(csvfile,fieldnames=fields)
        writer.writeheader()
        for error in errors:
            writer.writerow(error)


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
        response = []
        for t in track(asyncio.as_completed(tasks), total=len(tasks), description="Running the requests..."):
            r = await t
            if r is not None:
                response.append(r)
            
        
        #If there are errors, then save them in a csv file
        if response is not None:
            print()
            error_log(response)



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