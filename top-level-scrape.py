import traceback
import time
import requests
from bs4 import BeautifulSoup
import json

base_url = "https://archiveofourown.org"
params = "?show_comments=true&view_full_work=true&view_adult=true"

with open("works.json") as file:
    works = json.load(file)

header = {
  "Host": "archiveofourown.org",
  "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
  "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
  "Accept-Language": "en-US,en;q=0.5",
  "Accept-Encoding": "gzip, deflate, br",
  "Connection": "keep-alive",
  "Cookie": "hlsPlayback=on",
  "Upgrade-Insecure-Requests": "1",
  "Sec-Fetch-Dest": "document",
  "Sec-Fetch-Mode": "navigate",
  "Sec-Fetch-Site": "same-origin",
  "Sec-Fetch-User": "?1"
}


def request_webpage(url):
    req = 0;
    while (req == 0):
        try:
            req = requests.get(url, headers=header)
        except:
            print("> connection error, trying again")
    body = BeautifulSoup(req.text, 'html.parser').select('body')
    while len(body) == 0:
        print("> reached request limit, pausing for 5 minutes")
        time.sleep(300)
        req = requests.get(url, headers=header)
        body = BeautifulSoup(req.text, 'html.parser').select('body')
    return body[0]


def handle_single_work(url):
    print("> handling work {}".format(url))
    # start from page 1
    page = 1
    soup = request_webpage(base_url + url + params + "&page={}".format(page))
    thread_list = soup.find(id="comments_placeholder").find("ol", class_="thread")
    threads = thread_list.find_all("li", class_="comment", recursive=False)
    print("> reading comment pages...")
    # loop while page contains comments
    while (threads):
        # print progress
        if page % 50 == 0:
            print(".")
        else:
            print(".", end="", flush=True)
        # collect top-level threads
        thread_ids = ["/comments/{}".format(t["id"].split("_")[-1]) for t in threads]
        stack.extend(thread_ids)
        # move to next page
        page+=1
        soup = request_webpage(base_url + url + params + "&page={}".format(page))
        try:
            thread_list = soup.find(id="comments_placeholder").find("ol", class_="thread")
        except:
            # weird error, better check the url and see what's going on there
            print(base_url + url + params + "&page={}".format(page))
            exit()
        threads = thread_list.find_all("li", class_="comment", recursive=False)
    print(".")
    print("[{} total pages]".format(page))
    print("> found {} top-level threads".format(len(stack)))
    with open(f"top-level-threads-{url.replace("/", "")}.json", "w") as file:
        json.dump(stack, file, ensure_ascii=False, indent=2)
    return 0


for work in works:
    handle_single_work(work["name"])
