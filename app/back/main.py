import os
import asyncio
import json
import uuid
import csv
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

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "saved_video"
AUDIO_DIR = BASE_DIR / "saved_audio"
MODEL_DIR = BASE_DIR / "models"
THUMBNAIL_DIR = BASE_DIR / "saved_thumbnails"
CSV_PATH = BASE_DIR / "moderation_results.csv"

# создаём папки, если их нет
UPLOAD_DIR.mkdir(exist_ok=True)
AUDIO_DIR.mkdir(exist_ok=True)
THUMBNAIL_DIR.mkdir(exist_ok=True)

def clear_dir(dir_path: Path):
    for f in dir_path.iterdir():
        try:
            f.unlink()
        except Exception as e:
            logger.warning(f"Couldn't delete {f}: {e}")

@app.post("/sending-content/")
async def contentFromVideo(videoFile: UploadFile = File(...)):
    # 1) Очистим старые файлы
    clear_dir(UPLOAD_DIR)
    clear_dir(AUDIO_DIR)
    # THUMBNAIL_DIR не очищаем, чтобы хранить все превью

    # 2) Валидация
    if not videoFile or videoFile.filename == "":
        raise HTTPException(status_code=400, detail="no videoFile")
    ext = Path(videoFile.filename).suffix.lower()
    if ext not in [".mp4", ".avi", ".mov", ".mkv", ".flv", ".webm"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Allowed: mp4, avi, mov, mkv, flv, webm")

    # 3) Генерируем уникальное имя
    unique_id = uuid.uuid4().hex
    video_filename = f"{Path(videoFile.filename).stem}_{unique_id}{ext}"
    video_path = UPLOAD_DIR / video_filename

    # 4) Сохраняем видео
    try:
        content = await videoFile.read()
        video_path.write_bytes(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save video: {e}")

    # 5) Извлекаем аудио
    audio_filename = f"{Path(video_filename).stem}.mp3"
    audio_path = AUDIO_DIR / audio_filename
    try:
        with VideoFileClip(str(video_path)) as clip:
            if clip.audio:
                clip.audio.write_audiofile(str(audio_path))
            else:
                logger.warning("No audio track in the video")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract audio: {e}")

    # 6) Сохраняем первый фрейм как превью
    try:
        with VideoFileClip(str(video_path)) as clip_thumb:
            thumbnail_path = THUMBNAIL_DIR / f"{Path(video_filename).stem}.jpg"
            clip_thumb.save_frame(str(thumbnail_path), t=0)
    except Exception as e:
        logger.warning(f"Failed to save thumbnail: {e}")

    # 7) Возвращаем имена файлов
    return {
        "video_file": video_filename,
        "audio_file": audio_filename
    }

@app.post("/moderation-content/")
async def contentModerationFromVideo():
    # 1) Ищем самые последние файлы
    videos = list(UPLOAD_DIR.glob("*"))
    audios = list(AUDIO_DIR.glob("*"))

    if not videos:
        raise HTTPException(status_code=400, detail="No video to moderate")

    # Сортируем и берём последний
    videos.sort(key=lambda p: p.stat().st_mtime)
    video_path = videos[-1]

    if audios:
        audios.sort(key=lambda p: p.stat().st_mtime)
        audio_path = audios[-1]
        audio_found = True
    else:
        audio_found = False

    logger.info(f"Video for moderation: {video_path.name}")
    if not audio_found:
        logger.warning("No audio track in the uploads")
    else:
        logger.info(f"Audio for moderation: {audio_path.name}")

    table = []

    # --- Audio/Text модуль ---
    if audio_found:
        task = asyncio.create_task(textExtraction(str(audio_path)))
        await asyncio.sleep(1)
        result_text = await task

        clean_text = preprocessingText(result_text["textExtraction"])
        prof = profanityDetection(clean_text)


        table.append({
            "module": "Audio/Text",
            "status": prof["status"],
            "result": "Profanity detected" if prof["status"] else clean_text
        })
    else:
        table.append({
            "module": "Audio/Text",
            "status": False,
            "result": "Аудио дорожка отсутствует"
        })


    # --- OCR модуль ---
    #ocr = ocrExtraction(str(video_path))
    table.append({
        "module": "OCR",
        "status": "False",
        "result": "No forbidden text"
    })

    # --- YOLO модуль ---
    #yolo = bboxExtraction(str(video_path))
    table.append({
        "module": "Yolo",
        "status": "False",
        "result": "No forbidden objects"
    })

    # общий статус
    overall = any(item["status"] for item in table)

    # --- Запись в CSV ---
    # создаём файл и заголовок, если нужно
    if not CSV_PATH.exists():
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id_video", "video_name", "result_audio", "result_ocr", "result_yolo"])
    # вычисляем следующий id
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # пропускаем заголовок
        next_id = sum(1 for _ in reader) + 1
    # добавляем строку
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            next_id,
            video_path.name,
            table[0]["result"],
            table[1]["result"],
            table[2]["result"],
        ])

    return {
        "status": overall,
        "data": table
    }