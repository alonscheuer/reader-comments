import spacy
from spacy.tokens import Doc
import pandas as pd
from tqdm import tqdm

nlp = spacy.load("en_core_web_trf")

def masker(doc):
    ents = [ent.text for ent in doc.ents if ent.label_ in ['ORG', 'PERSON', 'GPE', 'PRODUCT', 'WORK_OF_ART', 'NORP', 'LOC', 'EVENT']]
    new_words = [token.ent_type_ if token.ent_type_ != '' else token.text for token in doc]
    spaces = [len(token.whitespace_) > 0 for token in doc]
    new_doc = Doc(doc.vocab, words=new_words, spaces=spaces)
    return new_doc.text, ents

data = pd.read_csv("spans.csv")
list_masked = []
list_ents = []

docs = nlp.pipe([str(t) for t in data["hasText"]])
for doc in tqdm(docs):
    masked_text, ents = masker(doc)
    list_masked.append(masked_text)
    list_ents.append(';'.join(ents))
    
data["maskedText"] = list_masked
data["entities"] = list_ents
data.to_csv("spans.csv")
