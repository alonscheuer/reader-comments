# Function-based Classification of Online Reader Comments on Archive of Our Own

`top-level-scrape.py` is used to collect top-level comments (supply a list of works in this file or in a separate `works` file).

`thread-scrape.py` is used to collect all comment spans from top-level comments and their replies.

`mask.py` is used to run named-entity extraction and masking

`context.py` is used to merge context for each span.

`ml.py` is used to train and evaluate an SVC model.

`train.py` is used to train and evaluate a BERT classifier.

`predict.py` is used to run the trained classifier on unannotated data.

`csv2owl.py` is used to export the comments and spans in an OWL-RDF format, for injection into an OWL ontology.

`infer.py` is used to apply inference rules in python instead of in Protege, if needed.
