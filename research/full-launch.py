import torch
import pandas as pd
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split



DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print("✅ DEVICE:", DEVICE)



trainDf = pd.read_csv("/home/retro0/cyberspace/projects/full-stack/diplom-2025/mediaModeration/research/labeledProfanity.csv")
trainDf["labels"] = trainDf["labels"].str.lower().str.strip()

ALLOWED_LABELS = ["profanity", "non profanity"]
trainDf = trainDf[trainDf["labels"].isin(ALLOWED_LABELS)].copy()

print("✅ Чистые метки:", trainDf["labels"].unique())

label_encoder = LabelEncoder()
label_encoder.fit(ALLOWED_LABELS)
trainDf["labels"] = label_encoder.transform(trainDf["labels"])

assert set(trainDf["labels"].unique()) == {0, 1}, "❌ Обнаружены лишние классы!"

train_data, val_data = train_test_split(trainDf, test_size=0.1, stratify=trainDf["labels"], random_state=42)
train_dataset = Dataset.from_pandas(train_data)
val_dataset = Dataset.from_pandas(val_data)



modelRubert = 'DeepPavlov/rubert-base-cased'
tokenizer = AutoTokenizer.from_pretrained(modelRubert)

def tokenize_function(example):
    return tokenizer(
        example["words"],
        truncation=True,
        padding="max_length",
        max_length=16
    )

tokenized_train = train_dataset.map(tokenize_function, batched=True)
tokenized_val = val_dataset.map(tokenize_function, batched=True)


model = AutoModelForSequenceClassification.from_pretrained(
    modelRubert,
    num_labels=2
)



def computeMetrics(p):
    preds = p.predictions.argmax(-1)
    labels = p.label_ids
    return {
        "accuracy": accuracy_score(labels, preds),
        "precision": precision_score(labels, preds),
        "recall": recall_score(labels, preds),
        "f1": f1_score(labels, preds)
    }



training_args = TrainingArguments(
    output_dir="/home/retro0/cyberspace/projects/full-stack/diplom-2025/mediaModeration/research/model-bert/rubert-obscene-detector",
    evaluation_strategy="epoch",
    save_strategy="no",
    logging_dir="/home/retro0/cyberspace/projects/full-stack/diplom-2025/mediaModeration/research/model-bert/logs",
    logging_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=128,
    num_train_epochs=4,
    fp16=True,
    dataloader_num_workers=8,
    dataloader_pin_memory=True
)



trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_val,
    tokenizer=tokenizer,
    compute_metrics=computeMetrics
)


trainer.train()
metrics = trainer.evaluate()
print("\n📊 Final Validation Metrics:")
for key, value in metrics.items():
    print(f"{key}: {value:.4f}")