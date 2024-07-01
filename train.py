import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer, EarlyStoppingCallback
from datasets import Dataset, DatasetDict
import numpy as np
import evaluate
from sklearn.metrics import classification_report, confusion_matrix

model_name = "unmasked"
masked = False
context = False

col_list = []
col_list.append("maskedText" if masked else "hasText")
if context:
    col_list.append("maskedContext" if masked else "context")
col_list.append("annotation")


labels = ['agreement', 'answer', 'appreciation', 'commitment', 'community_interaction', 'emotion', 'entertainment', 'feedback', 'interpretation', 'none', 'personal_story', 'question']
id2label = {k: v for k, v in enumerate(labels)}
label2id = {v: k for k, v in enumerate(labels)}

def load_data(split):
    data = pd.read_csv(f"{split}.csv")[col_list]
    if context:
        # data[col_list[0]] is the text
        # data[col_list[1]] is the context
        data[col_list[0]] = ["PREV: " + str(ctx) + "\nCURRENT: " + str(t) for t, ctx in zip(data[col_list[0]], data[col_list[1]])]
    ds = Dataset.from_pandas(data, preserve_index=False)
    ds = ds.rename_column("annotation", "labels")


ds_splits = DatasetDict({
    "train": load_data("train"),
    "valid": load_data("valid"),
    "test": load_data("test")
})

model_id = "distilbert/distilbert-base-cased"
#model_id = "FacebookAI/roberta-large"
num_epochs = 10
tokenizer = AutoTokenizer.from_pretrained(model_id)

def tokenize_function(examples):
    return tokenizer(examples["hasText"], max_length=512, padding="max_length", truncation=True)


tokenized_datasets = ds_splits.map(tokenize_function, batched=True)

model = AutoModelForSequenceClassification.from_pretrained(model_id, num_labels=len(labels), id2label=id2label, label2id=label2id)

training_args = TrainingArguments(
    output_dir="test_trainer",
    evaluation_strategy="epoch",
    num_train_epochs=num_epochs,
    save_total_limit=3,
    save_strategy="epoch",
    metric_for_best_model="eval_loss",
    load_best_model_at_end=True,
    greater_is_better=False
)

metric = evaluate.load("accuracy")

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return metric.compute(predictions=predictions, references=labels)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets["train"],
    eval_dataset=tokenized_datasets["valid"],
    compute_metrics=compute_metrics,
    callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
)

trainer.train()
trainer.save_model(output_dir="OUTPUT_DIR/" + model_id.replace("/", "_") + "_" + model_name + "_" + str(num_epochs))

preds = np.argmax(trainer.predict(test_dataset=tokenized_datasets["test"]).predictions, axis=-1)
print(classification_report(tokenized_datasets["test"]["labels"], preds))
print(confusion_matrix(tokenized_datasets["test"]["labels"], preds))
