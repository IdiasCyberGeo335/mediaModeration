import os
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException
from moviepy import VideoFileClip
from loguru import logger

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
    pass