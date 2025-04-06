import streamlit as st
import requests
import base64


"""
Инициализация ручек
"""

URLposting = "http://localhost:8000/sending-content/"
URLprocessing = "http://localhost:8000/moderation-contetnt/"



#st.set_page_config(page_title="Download Page", layout="centered")

# Инжектируем CSS для стилизации основного контейнера приложения и виджетов
st.markdown("""
    <style>
        /* Основной контейнер приложения */
        [data-testid="stAppViewContainer"] {
            background-color: #202024;
            border-radius: 8px;
            padding: 40px;
            box-shadow: 0px 0px 20px rgba(0, 0, 0, 0.5);
            max-width: 900px;
            margin: 40px auto;
        }
        /* Общий фон приложения */
        .stApp {
            background-color: #18181b;
            color: #fff;
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        }
        /* Заголовок страницы */
        .download-header {
            text-align: center;
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 30px;
            color: #9146FF;
        }
        /* Контейнер, оборачивающий видео для рамки */
        .video-wrapper {
            margin-top: 20px;
            border: 2px solid #9146FF;
            border-radius: 8px;
            padding: 10px;
        }
        /* Переопределение стилей стандартной кнопки Streamlit */
        div.stButton > button {
            background-color: #6441a5;
            color: #fff;
            padding: 12px 25px;
            font-size: 16px;
            border: none;
            border-radius: 4px;
            margin: 10px auto;
            display: block;
        }
    </style>
""", unsafe_allow_html=True)

# Заголовок страницы
st.markdown('<h1 class="download-header">Download Page</h1>', unsafe_allow_html=True)

# Загрузчик видео
upload_file = st.file_uploader("MILFS", type=["mp4", "mov", "avi"])



if upload_file is not None:
    # Оборачиваем видео в контейнер с рамкой
    st.markdown('<div class="video-wrapper">', unsafe_allow_html=True)
    st.video(upload_file)
    st.markdown('</div>', unsafe_allow_html=True)

    files = {
        "videoFile" : (upload_file.name, upload_file, upload_file.type)

    }


    response = requests.post(URLposting, files=files) 



# Кнопка "Обработать" (пока без функционала)
if st.button("Обработать"):
    st.info("Видеофайл отправлен на бэкэнд!")
    response = requests.post(URLprocessing)