import pandas as pd
import textwrap

ann = pd.read_csv("annotated_with_preds_and_ents.csv").to_dict("records")
unann = pd.read_csv("unannotated_with_preds_and_ents.csv").to_dict("records")
spans = sorted(ann + unann, key=lambda x: x["name"])

tmp = pd.read_json("comments2.json")
comments = sorted(tmp[tmp["work"] != "\/works\/30346350"].to_dict("records"), key=lambda x: x["name"])

def span2owl(span):
    span_name = span["name"].split("#")[-1]
    comment_name = span["partOf"].split("#")[-1]
    opening = f"    <owl:NamedIndividual rdf:about=\"http://www.semanticweb.org/alon/ontologies/2024/2/comment#{span_name}\">"
    closing = "    </owl:NamedIndividual>"
    fields = [
        "<rdf:type rdf:resource=\"http://www.semanticweb.org/alon/ontologies/2024/2/comment#Span\"/>",
        f"<partOf rdf:resource=\"http://www.semanticweb.org/alon/ontologies/2024/2/comment#{comment_name}\"/>",
        f"<spanOrder rdf:datatype=\"http://www.w3.org/2001/XMLSchema#int\">{span['order']}</spanOrder>",
        f"<spanStart rdf:datatype=\"http://www.w3.org/2001/XMLSchema#int\">{span['start']}</spanStart>",
        f"<spanEnd rdf:datatype=\"http://www.w3.org/2001/XMLSchema#int\">{span['end']}</spanEnd>",
        f"<hasText rdf:datatype=\"http://www.w3.org/2001/XMLSchema#string\">{str(span['hasText']).replace('&', '&amp;').replace('<','&lt;').replace('>','&gt;')}</hasText>"
    ]
    if span['prediction'] != "none":
        fields.append(f"<hasFunction rdf:resource=\"http://www.semanticweb.org/alon/ontologies/2024/2/comment#{span['prediction']}\"/>")
    if not pd.isnull(span["entities"]):
        entities = ";".join(set([e.lower() for e in span["entities"].split(";")])).replace('&', '&amp;')
        fields.append(f"<about rdf:datatype=\"http://www.w3.org/2001/XMLSchema#string\">{entities}</about>")
    fields = textwrap.indent("\n".join(fields), '        ')
    return "\n".join([opening, fields, closing])


def thread2owl(root):
    root_name = root["name"].split("#")[-1]
    thread_name = "t_" + root_name
    opening = f"    <owl:NamedIndividual rdf:about=\"http://www.semanticweb.org/alon/ontologies/2024/2/comment#{thread_name}\">"
    closing = "    </owl:NamedIndividual>"
    fields = [
        "<rdf:type rdf:resource=\"http://www.semanticweb.org/alon/ontologies/2024/2/comment#Thread\"/>",
        f"<hasRoot rdf:resource=\"http://www.semanticweb.org/alon/ontologies/2024/2/comment#{root_name}\"/>"
    ]
    fields = textwrap.indent("\n".join(fields), '        ')
    return "\n".join([opening, fields, closing])


def comment2owl(comment):
    comment_name = comment["name"].split("#")[-1]
    opening = f"    <owl:NamedIndividual rdf:about=\"http://www.semanticweb.org/alon/ontologies/2024/2/comment#{comment_name}\">"
    closing = "    </owl:NamedIndividual>"
    fields = [
        "<rdf:type rdf:resource=\"http://www.semanticweb.org/alon/ontologies/2024/2/comment#Comment\"/>"
    ]
    if not pd.isnull(comment["hasParent"]):
        parent_name = comment["hasParent"].split("#")[-1]
        fields.append(f"<hasParent rdf:resource=\"http://www.semanticweb.org/alon/ontologies/2024/2/comment#{parent_name}\"/>")
        fields = textwrap.indent("\n".join(fields), '        ')
        return "\n".join([opening, fields, closing])
    else:
        thread = thread2owl(comment)
        fields = textwrap.indent("\n".join(fields), '        ')
        return "\n".join([thread, opening, fields, closing])

inds = "\n\n".join([
    "\n".join([comment2owl(c) for c in comments]),
    "\n".join([span2owl(s) for s in spans])
])

with open("individuals.txt", "w") as file:
    file.write(inds)
