import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset
import numpy as np

model_id = "OUTPUT_DIR/comment-classifier"

data = pd.read_csv("to_annotate.csv")
ds = Dataset.from_dict({"text": data["maskedText"], "label": [0 for i in data["maskedText"]]})
tokenizer = AutoTokenizer.from_pretrained("distilbert/distilbert-base-cased")
def tokenize_function(examples):
    return tokenizer(examples["text"], max_length=512, padding="max_length", truncation=True)

tokenized_ds = ds.map(tokenize_function, batched=True)

model = AutoModelForSequenceClassification.from_pretrained(model_id)

trainer = Trainer(model=model)

output = trainer.predict(test_dataset=tokenized_ds)
preds = np.argmax(output.predictions, axis=-1)
pred_labels = [labels[p] for p in preds]
data['predictions'] = pred_labels
data.to_csv("predictions.csv")
