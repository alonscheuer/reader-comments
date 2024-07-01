import traceback
import time
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from spacy.lang.en import English

nlp = English()
nlp.add_pipe("sentencizer", config={"punct_chars": ["\n", ".", "!", "?"]})

base_url = "https://archiveofourown.org"
params = "?show_comments=true&view_full_work=true&view_adult=true"

stack = pd.read_json("top-level-threads.json").to_dict("records")

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


def handle_spans(comment):
    comment["hasPart"] = [];
    doc = nlp(comment["content"])
    doc_sents = [sent.text.replace("\n", "") for sent in doc.sents]
    doc_sents = [sent for sent in doc_sents if len(sent) > 0]
    comment_spans = []
    for i_sent, sent in enumerate(doc_sents, start=1):
        span_name = "{}_{}".format(comment["name"], i_sent)
        comment["hasPart"].append(span_name)
        comment_spans.append({"name": span_name,
                      "partOf": comment["name"],
                      "order": i_sent,
                      "start": sent.start_char,
                      "end": sent.end_char,
                      "hasText": sent.text})
    return comment_spans


def handle_single_thread(comment):
    url = comment["name"]
    parent = comment.get("parent")
    comment_url = "{}#comment_{}".format(url, url.split("/")[-1])
    data = {}
    soup = request_webpage(base_url + url)
    thread = soup.find(id="main")
    data["work"] = thread.find("h3").find("a")["href"]
    root = comment_list[0]
    # collect root comment info
    data["name"] = comment_url
    if not root.find("blockquote"):
        return 0
    data["content"] = root.find("blockquote").get_text("\n")
    data["chapter"] = root.find(class_="parent").get_text().replace("\n", " ").strip().replace("on ", "").lower().replace(" ", "-")
    if parent:
        data["hasParent"] = parent
    comment_spans = pd.DataFrame(handle_spans(data))
    comment_spans.to_json("spans.jsonl", mode="a", lines=True, orient="records", force_ascii=False)
    comment_data = pd.DataFrame.from_dict(data, orient="index").unstack().unstack()
    comment_data.to_json("comments.jsonl", mode="a", lines=True, orient="records", force_ascii=False)
    # collect direct replies
    comment_list = thread.find("ol").find_all("li", recursive=False)
    if len(comment_list) > 1:
        reply_list = comment_list[1].find("ol").find_all("li", class_="comment", recursive=False)
        reply_urls = [{"name": "/comments/{}".format(reply["id"].split("_")[1]), "parent": comment_url} for reply in reply_list]
        stack.extend(reply_urls)


counter = 1
while len(stack) > 0:
    if counter % 50 == 0:
        print(".")
    else:
        print(".", end="", flush=True)
    handle_single_thread(stack.pop())
    with open("thread-stack.json", "w") as file:
        json.dump(stack, file, ensure_ascii=False, indent=2)
    counter = counter + 1
