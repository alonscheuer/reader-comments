import pprint
import requests
from bs4 import BeautifulSoup
import json
# import spacy
from spacy.lang.en import English

pp = pprint.PrettyPrinter(indent=2)

nlp = English()
nlp.add_pipe("sentencizer", config={"punct_chars": ["\n", ".", "!", "?"]})
# nlp = spacy.load("en_core_web_sm")

base_url = "https://archiveofourown.org"
params = "?show_comments=true&view_full_work=true&view_adult=true"
works = []
comment_pages = []
threads = []
comments = []
spans = []
to_process = []

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

def handle_spans(comment):
    comment["hasPart"] = [];
    doc = nlp(comment["content"])
    for i_sent, sent in enumerate(doc.sents):
        span_name = "{}_{}".format(comment["name"], i_sent + 1)
        comment["hasPart"].append(span_name)
        spans.append({"name": span_name,
                      "partOf": comment["name"],
                      "order": i_sent + 1,
                      "start": sent.start_char,
                      "end": sent.end_char,
                      "hasText": sent.text})

def handle_single_thread(url):
    print(url)
    comment_url = "{}#comment_{}".format(url, url.split("/")[-1])
    threads.append({"name": url,
                    "hasRoot": comment_url})
    data = {}
    req = requests.get(base_url + url, headers=header)
    soup = BeautifulSoup(req.text, 'html.parser').select('body')[0]
    thread = soup.find(id="main")
    data["work"] = thread.find("h3").find("a")["href"]
    comment_list = thread.find("ol").find_all("li", recursive=False)
    root = comment_list[0]
    # collect root comment info
    data["name"] = comment_url
    data["content"] = root.find("blockquote").get_text("\n")
    data["chapter"] = root.find(class_="parent").get_text().replace("\n", " ").strip().replace("on ", "").lower().replace(" ", "-")
    data["timestamp"] = root.find(class_="posted datetime").get_text().replace("\n", " ").strip()
    if root.find("h4").find("a"):
        data["user"] = root.find("a")["href"]
    else:
        data["user"] = root.find("span").get_text() + " (Guest)"
    handle_spans(data)
    comments.append(data)
    # collect direct replies
    if len(comment_list) > 1:
        reply_list = comment_list[1].find("ol").find_all("li", class_="comment", recursive=False)
        reply_urls = ["/comments/{}".format(reply["id"].split("_")[1]) for reply in reply_list]
        to_process.extend(reply_urls)

def handle_single_work(url):
    works.append({"name": url})
    page = 1
    req = requests.get(base_url + url + params + "&page={}".format(page), headers=header)
    soup = BeautifulSoup(req.text, 'html.parser').select('body')[0]
    thread_list = soup.find(id="comments_placeholder").find("ol", class_="thread")
    threads = thread_list.find_all("li", class_="comment", recursive=False)
    stack = []
    while (threads):
        thread_ids = ["/comments/{}".format(t["id"].split("_")[-1]) for t in threads]
        stack.extend(thread_ids)

        page+=1
        req = requests.get(base_url + url + params + "&page={}".format(page), headers=header)
        soup = BeautifulSoup(req.text, 'html.parser').select('body')[0]
        thread_list = soup.find(id="comments_placeholder").find("ol", class_="thread")
        threads = thread_list.find_all("li", class_="comment", recursive=False)
    while len(stack) > 0:
        handle_single_thread(stack.pop())


handle_single_work("/works/54597028")
# handle_single_work("/works/54618250")
# handle_single_work("/works/54380743")
pp.pprint(threads)
pp.pprint(comments)
pp.pprint(spans)

