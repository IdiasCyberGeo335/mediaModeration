import os
import asyncio
import json
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException
from moviepy import VideoFileClip
from loguru import logger

from scripts.textDetector import textExtraction
from scripts.ocrDetector import ocrExtraction
from scripts.yoloDetector import bboxExtraction
from scripts.profanityDetector import profanityDetection

from scripts.preprocessing import preprocessingText

app = FastAPI()

"""
Инициализация путей:
    - BASE_DIR -> корневая директория для main.py
    - UPLOAD_DIR -> директория для загрузки видео 
    - MODEL_DIR -> путь к моделям относительно корневой директории
"""

BASE_DIR = Path(__file__).resolve().parent

UPLOAD_DIR = BASE_DIR / "saved_video"
os.makedirs(UPLOAD_DIR, exist_ok=True)

AUDIO_DIR = BASE_DIR / "saved_audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

MODEL_DIR = BASE_DIR / "models"



@app.post("/sending-content/")
async def contentFromVideo(videoFile: UploadFile = File(...)):
    """если не получили видео, то HTTPException"""
    if not videoFile:
        raise HTTPException(status_code=400, detail="no videoFile")
    
    """если получили видео, но оно пустое, то HTTPException"""
    if videoFile.filename == "":
        raise HTTPException(status_code=400, detail="no selected videoFile")
    
    """если получили видео и всё ок, проверяем расширение"""
    videoFileExtention = Path(videoFile.filename).suffix
    if videoFileExtention not in [".mp4", ".MP4", ".avi", ".mov", ".mkv", ".flv", ".webm"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Files alloweded: mp4, avi, mov")
    
    """генерируем путь для сохранения файла"""
    videoFilePath = os.path.join(UPLOAD_DIR, videoFile.filename)

    try:
        with open(videoFilePath, "wb") as buffer:
            content = await videoFile.read()
            buffer.write(content)
        
        """извлекаем аудио-дорожку"""
        audioFileName = f"{Path(videoFile.filename).stem}.mp3"
        audioFilePath = AUDIO_DIR / audioFileName

        with VideoFileClip(str(videoFilePath)) as clipVideo:
            clipAudio = clipVideo.audio
            if clipAudio:
                clipAudio.write_audiofile(str(audioFilePath))
                clipAudio.close()
            else:
                logger.info(f"Audio doesnt exist")


    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file {e}")
    

@app.post("/moderation-contetnt/")
async def contentModerationFromVideo():
    logger.info(f"Searching files...")

    videoFile = list(UPLOAD_DIR.glob("*"))
    audioFile = list(AUDIO_DIR.glob("*"))

    videoPath = videoFile[0]
    audioPath = audioFile[0]

    logger.info(f"videoFile Detected: {videoPath}")
    logger.info(f"audioFile Detected: {audioPath}")

    
    logger.info(f"Launching detectors...")

    """
    Отработка модуля 1:
        -Извлечение текста из аудио -> детекция запрещённых слов
    """
    logger.info(f"Launching TextExtractor...")
    taskTextExtractor = asyncio.create_task(textExtraction(str(audioPath)))

    await asyncio.sleep(6)
    taskTextExtractor = await taskTextExtractor
    logger.info(f"{type(taskTextExtractor)}")
    logger.info(f"{taskTextExtractor}")
    logger.info(f"TextExtractor: {taskTextExtractor['textExtraction']}")

    taskTextExtractor['textExtraction'] = preprocessingText(taskTextExtractor['textExtraction'])
    logger.info(f"CURRENT taskPreprocessingText: {taskTextExtractor}")
    taskProfanityDetector = (profanityDetection(str(taskTextExtractor['textExtraction'])))
    taskTextExtractor = taskTextExtractor | taskProfanityDetector
    logger.info(f"taskTextExtractor: {taskTextExtractor}")

    if taskTextExtractor.get("status") is True:
        tableData = [
            {
                "module": "Audio",
                "status": taskTextExtractor.get("status"),
                "result": taskTextExtractor.get("textExtraction")
                #"result": "Profanity detected"
            },
            {
                "module": "OCR",
                "status": False,
                "result": "Forbidden content didnt find"
            },
            {
                "module": "Yolo",
                "status": False,
                "result": "Forbidden content didnt find"
            }
        ]
        return {"status": True, "data": tableData}
    else:
        return {"status": False, "error": "ERROR"}










    
    #logger.info(f"Launching taskAudio...")
    #taskOCR = asyncio.create_task(ocrExtraction(str(videoPath)))
    #logger.info(f"Launching taskAudio...")
    #taskVideo = asyncio.create_task(bboxExtraction(str(videoPath)))