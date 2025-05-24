import streamlit as st
import pandas as pd
from pathlib import Path

# --- Настройки путей ---
# Путь к корню проекта (две директории вверх от текущего файла)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
# Путь к бэкенду
BACK_DIR = PROJECT_ROOT / "back"
CSV_PATH = BACK_DIR / "moderation_results.csv"
# Директория с превью (jpg)
THUMBNAIL_DIR = BACK_DIR / "saved_thumbnails"

# Конфигурация страницы
st.set_page_config(page_title="История модерации - YAPPY", layout="wide")

# CSS для стилизации
st.markdown("""
    <style>
        [data-testid=\"stAppViewContainer\"] {
            background-color: #202024;
            border-radius: 8px;
            padding: 40px;
            box-shadow: 0px 0px 20px rgba(0, 0, 0, 0.5);
            max-width: 900px;
            margin: 40px auto;
        }
        .stApp {
            background-color: #18181b;
            color: #fff;
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        }
        .download-header {
            text-align: center;
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 30px;
            color: #9146FF;
        }
        .thumbnail {
            object-fit: cover;
            width: 120px;
            height: 80px;
            border: 2px solid #9146FF;
            border-radius: 4px;
        }
    </style>
""", unsafe_allow_html=True)

# Заголовок страницы
st.markdown('<h1 class=\"download-header\">История модерации</h1>', unsafe_allow_html=True)

# Проверка наличия CSV
if not CSV_PATH.exists():
    st.info(f"CSV не найден по пути: {CSV_PATH}")
    st.stop()

# Чтение данных
try:
    df = pd.read_csv(CSV_PATH, dtype=str)
except Exception as e:
    st.error(f"Не удалось прочитать CSV: {e}")
    st.stop()

if df.empty:
    st.info("CSV пуст. Нет записей для отображения.")
    st.stop()

# Отображение каждой записи
for _, row in df.iterrows():
    cols = st.columns([1, 2, 2, 2])

    # Превью видео (jpg)
    with cols[0]:
        thumb_name = Path(row.get("video_name", "")).with_suffix('.jpg').name
        thumb_path = THUMBNAIL_DIR / thumb_name
        if thumb_path.exists():
            st.image(str(thumb_path), use_container_width=False, width=120)
        else:
            st.error(f"Превью не найдено: {thumb_path}")
        st.caption(f"ID: {row.get('id_video', '-')}")

    # Результат Audio/Text
    with cols[1]:
        st.subheader("Audio/Text")
        st.write(row.get("result_audio", "-"))

    # Результат OCR
    with cols[2]:
        st.subheader("OCR")
        st.write(row.get("result_ocr", "-"))

    # Результат YOLO
    with cols[3]:
        st.subheader("Yolo")
        st.write(row.get("result_yolo", "-"))

    st.markdown("---")