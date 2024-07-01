import pandas as pd
from tqdm import tqdm

data = pd.read_csv("data.csv")
comments = pd.read_json("comments.json")
spans = pd.read_csv("spans.csv")

ctx_type = []
ctx_spans = []
context = []
masked = []

for span_comment, span_order in tqdm(zip(data["partOf"], pd.to_numeric(data["order"]))):
    comment = comments[comments["name"] == span_comment]
    parent_comment_name = comment["hasParent"].values[0]
    # if this is not the first span in its comment, grab the previous span from this comment
    if span_order > 1:
        prev_span = spans[(spans["partOf"] == span_comment) & (spans["order"] == (span_order-1))]
        ctx_type.append("same")
        ctx_spans.append(prev_span["name"].values[0])
        context.append(prev_span["hasText"].values[0])
        masked.append(prev_span["maskedText"].values[0])
    # if this is the first span, and this comment replies to another comment, take the last span from the previous comment
    elif parent_comment_name != None:
        prev_comment = comments[comments["name"] == parent_comment_name]
        prev_span_name = prev_comment["hasPart"].values[0][-1]
        prev_span = spans[spans["name"] == prev_span_name]
        ctx_type.append("diff")
        ctx_spans.append(prev_span["name"].values[0])
        context.append(prev_span["hasText"].values[0])
        masked.append(prev_span["maskedText"].values[0])
    # otherwise, don't take anything
    else:
        ctx_type.append("none")
        ctx_spans.append(None)
        context.append("")
        masked.append("")

data["contextType"] = ctx_type
data["contextSpan"] = ctx_spans
data["context"] = context
data["maskedContext"] = masked
data.to_csv("data_with_context.csv")
