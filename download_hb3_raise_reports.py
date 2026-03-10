import os
import aiohttp
import asyncio
from tqdm import tqdm
import aiofiles

# Assuming the directory name is stored in the following variable
ba_increase_raise_mechanism_reports = "HB 3 Raise Reports"

# Make sure directory exists, if not, create it
if not os.path.exists(ba_increase_raise_mechanism_reports):
    os.makedirs(ba_increase_raise_mechanism_reports)

# Read the file containing URLs
with open('xlsx_links.txt', 'r') as f:
    urls = f.read().splitlines()

# Set the semaphore to limit the number of requests
semaphore = asyncio.Semaphore(8)

# Create a progress bar
pbar = tqdm(total=len(urls))

async def download_file(session, url):
    # Get file name from URL
    file_name = url.split("/")[-1]

    # Check if file already exists and add increment if it does
    if os.path.exists(os.path.join(ba_increase_raise_mechanism_reports, file_name)):
        base, ext = os.path.splitext(file_name)
        i = 1
        while os.path.exists(os.path.join(ba_increase_raise_mechanism_reports, f"{base}_{i}{ext}")):
            i += 1
        file_name = f"{base}_{i}{ext}"

    # Download and save the file
    async with semaphore:
        async with session.get(url) as response:
            if response.status == 200:
                f = await aiofiles.open(os.path.join(ba_increase_raise_mechanism_reports, file_name), mode='wb')
                await f.write(await response.read())
                await f.close()

    # Update the progress bar
    pbar.update(1)

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            task = asyncio.ensure_future(download_file(session, url))
            tasks.append(task)
        await asyncio.gather(*tasks)

# Run the async main function
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
pbar.close()
