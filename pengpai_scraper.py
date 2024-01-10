import asyncio
import aiofiles
from aiocsv import AsyncWriter
from aiohttp import ClientSession
import re
import orjson
import argparse

assigner_jobs_done = None
workers_jobs_done = None

content_headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,ja;q=0.6,hy;q=0.5',
    'Cache-Control': 'max-age=0',
    'Referer': 'https://www.thepaper.cn/channel_27392',
    'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Linux"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
pattern = re.compile(
    r'(?<=<script id="__NEXT_DATA__" type="application/json">).+(?=</script>)')


async def force_fetch_url(session: ClientSession, url_id, retry):
    if retry < 0:
        return False

    task_url = f"https://www.thepaper.cn/newsDetail_forward_{url_id}"
    try:
        async with session.get(task_url, headers=content_headers, allow_redirects=False) as resp:
            if resp.status != 200:
                return False

            html = await resp.text(encoding='utf-8')
            match = re.search(pattern, html)
            if not match:
                return False
            extracted_text = match.group()  # Extract the matched content
            page_json = orjson.loads(extracted_text)
            content_detail = page_json["props"]["pageProps"]["detailData"].get(
                "contentDetail")
            if not content_detail:
                return False
            content = content_detail.get("content")
            title = content_detail.get("name")
            author = content_detail.get("author")
            publish_time_string = content_detail.get("pubTime")
            publish_time_int = content_detail.get("publishTime")
            source = content_detail.get("source")
            if not (content and title and publish_time_string and publish_time_int) or content == "":
                if content:
                    print(content_detail)
                return False
            content = re.sub(r'<[^>]*>', '', content.replace("&nbsp;", "")
                             ).replace(",", "，").replace("\u3000", "")
            date = publish_time_string.split()[0]
            newline = [
                task_url,  # "link"
                url_id,  # number
                title,  # title
                author,  # author
                date,  # date
                publish_time_int,  # timestamp
                content,  # content
                len(content),  # content_length
                source  # source_info
            ]
            print(f"{url_id}...ok")
            return newline
    except BaseException as e:
        print(str(e))
        print(f'retrying {url_id}, remaining {retry}')
        retry -= 1
        await asyncio.sleep(5)
        return await force_fetch_url(session, url_id, retry)


async def worker(session: ClientSession, tasks_queue: asyncio.Queue, results_queue: asyncio.Queue):
    global assigner_jobs_done, workers_jobs_done
    
    while not (tasks_queue.empty() and assigner_jobs_done):
        url = await tasks_queue.get()
        new_csv_line = await force_fetch_url(session, url, 5)
        if new_csv_line:
            await results_queue.put(new_csv_line)
        tasks_queue.task_done()
    workers_jobs_done -= 1
    if not workers_jobs_done:
        await results_queue.put(False)
    print(f"worker {workers_jobs_done}: jobs done")


async def assigner(tasks_queue: asyncio.Queue, range_from, range_to):
    global assigner_jobs_done
    while range_from < range_to + 1:
        if GLOBAL_REQUEST_DELAY:
            await asyncio.sleep(GLOBAL_REQUEST_DELAY)
        await tasks_queue.put(range_from)
        range_from += 1
    assigner_jobs_done = True


async def writer(results_queue: asyncio.Queue, csv_file):
    global workers_jobs_done
    async with aiofiles.open(csv_file, 'w') as f:
        writer = AsyncWriter(f)
        await writer.writerow(["link", "number", "title", "author", "date", "timestamp", "content", "content_length", "source_info"])
        while not (workers_jobs_done == 0 and results_queue.empty):
            result = await results_queue.get()
            if not result:
                break
            await writer.writerow(result)
            results_queue.task_done()


async def main(pool_size, range_from, range_to, csv_file):
    global workers_jobs_done
    tasks_queue = asyncio.Queue(pool_size * 20)
    results_queue = asyncio.Queue()
    workers_jobs_done = pool_size
    async with ClientSession() as session:
        workers = [asyncio.create_task(worker(session, tasks_queue, results_queue))
                   for _ in range(pool_size)]
        await asyncio.gather(assigner(tasks_queue, range_from, range_to), writer(results_queue, csv_file), *workers)


POOL_SIZE = 2
GLOBAL_REQUEST_DELAY = 0
CSV_FOLDER = "./"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Process range values")
    parser.add_argument("-from", dest="from_val", type=int, help="Starting value")
    parser.add_argument("-to", dest="to_val", type=int, help="Ending value")
    args = parser.parse_args()

    if args.from_val is None or args.to_val is None:
        print("Please provide both -from and -to values")
    else:
        range_from = args.from_val
        range_to = args.to_val
        csv_file = f"{CSV_FOLDER}pengpai_data_beta_from_{range_from}_to_{range_to}.csv"
        asyncio.run(main(POOL_SIZE, range_from, range_to, csv_file))
