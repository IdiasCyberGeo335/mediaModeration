import os
from loguru import logger
from pathlib import Path
import torch
import whisper
import asyncio

BASE_DIR = Path(__file__).parent.parent
WHISPER_DIR = BASE_DIR / "models/whisper/whisper_medium_full.pth"

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
logger.info(f"Init DEVICE for Whisper: {DEVICE}")

async def textExtraction(audioPath: str):
    logger.info(f"textExtraction -> audioPath: {audioPath}")
    logger.info("Init whisper...")
    whisperLaunch = torch.load(WHISPER_DIR, map_location=DEVICE)
    logger.info("Whisper transcription...")
    
    """Extracting logic:"""
    result = whisperLaunch.transcribe(audioPath, word_timestamps=True)

    logger.info(f"Result of extracting: {result}")
    logger.info(f"Text full extracting: {result['text']}")

    wordTimestamps = {}

    for segment in result['segments']:
        for wordInfo in segment['words']:
            word = wordInfo['word']
            startTime = wordInfo['start']
            endTime = wordInfo['end']
            wordTimestamps[word] = (startTime, endTime)

    """for word, (startTime, endTime) in wordTimestamps.items():
        print(f"Слово '{word}', Начало: {startTime:.2f}s, Конец {endTime:.2f}s")"""
    
    return {
        "textExtraction": result['text'],
        "segments & wordTimestamps": "none"
    }