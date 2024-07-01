import pandas as pd
from tqdm import tqdm

spans = pd.read_csv("spans.csv")
comments = sorted(pd.read_csv("comments.csv").to_dict("records"), key=lambda x: x["name"])

# assign a thread for each top-level comment
threads = []
for comment in comments:
    if pd.isnull(comment["hasParent"]):
        thread_name = comment["name"].split("#")[0]
        threads.append({"name": thread_name, "hasRoot": comment["name"]})
        comment["inThread"] = thread_name
        comment["level"] = 0

# assign threads for replies
for comment in tqdm(comments, desc="assign thread"):
    if not pd.isnull(comment["hasParent"]):
        ancestor = next((c for c in comments if c["name"] == comment["hasParent"]), None)
        level = 1
        # go up until an already assigned comment is found
        while not "inThread" in ancestor:
            parentName = ancestor["hasParent"]
            next_ancestor = next((c for c in comments if c["name"] == parentName), None)
            level = level + 1
            if next_ancestor == None:
                break
            else:
                ancestor = next_ancestor
        if "inThread" in ancestor:
            comment["inThread"] = ancestor["inThread"]
        if "level" in ancestor:
            comment["level"] = ancestor["level"] + 1
        else:
            comment["level"] = level

# assign span depths
def span_level(span):
    comment = next((c for c in comments if c["name"] == span["partOf"]), None)
    if comment != None:
        return comment["level"]
    else:
        return None

print("sorting by depth...")
comments.sort(key = lambda c: c["level"])
spans.sort(key = lambda s: span_level(s))

# apply backward inference rules
for span in tqdm(spans, desc="infer backwards"):
    comment = next((c for c in comments if c["name"] == span["partOf"]), None)
    if comment != None:
        span["inThread"] = comment["inThread"]
        if span["prediction"] in ["agreement", "answer"]:
                if not pd.isnull(comment["hasParent"]):
                    parent = next((c for c in comments if c["name"] == comment["hasParent"]), None)
                    if parent != None:
                        parentSpans = [s for s in spans if s["partOf"] == parent["name"]]
                        if span["prediction"] == "agreement":
                            span["additional_functions"] = list(set([s["prediction"] for s in parentSpans if s["prediction"] not in ["agreement", "answer"]]))
                        span["additional_entities"] = list(set(";".join([str(s["entities"]) for s in parentSpans]).split(";")))

pd.DataFrame(spans).to_csv("spans_inferred.csv", index=False)
pd.DataFrame(comments).to_csv("comments_inferred.csv", index=False)
