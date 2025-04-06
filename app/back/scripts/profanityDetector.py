import torch

from pathlib import Path
from loguru import logger
import torch.nn.functional as F
from transformers import AutoModelForSequenceClassification



BASE_DIR = Path(__file__).parent.parent
BERT_DIR = BASE_DIR / "models/bert/model.pt"

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
logger.info(f"Init DEVICE for BERT: {DEVICE}")



checkpoint = torch.load(BERT_DIR, map_location=DEVICE)
model = AutoModelForSequenceClassification.from_config(checkpoint['model_config'])
model.load_state_dict(checkpoint["model_state_dict"])
model.to(DEVICE)
model.eval()
tokenizer = checkpoint["tokenizer"]

id2label = {0: "nonprofanity", 1: "profanity"}



def predict_label(text: str):
    # Токенизация входного текста
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding="max_length",
        max_length=16
    ).to(DEVICE)
    
    # Предсказание с использованием модели
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        predicted_class_id = logits.argmax(dim=-1).item()
    
    return id2label[predicted_class_id]


def profanityDetection(textForModeration: str):
    """
    Метки:
        - 0 -> обычное слово;
        - 1 -> запрещённое словож
    """
    tokensForTextForModeration = textForModeration.split()
    logger.info(f"tokensForTextForModeration: {tokensForTextForModeration}")

    wordTracker = ""
    statusBoolean = False
    detected = {"profanity": wordTracker, "status": statusBoolean}
    
    for i in range(len(tokensForTextForModeration)):
        logger.info(f"Tokens class: {tokensForTextForModeration[i]}, {predict_label(tokensForTextForModeration[i])}")
        if predict_label(tokensForTextForModeration[i]) == "profanity":
            detected["profanity"] = tokensForTextForModeration[i]
            detected["status"] = True
    
    logger.info(f"Detection Result: {detected}")
    return detected