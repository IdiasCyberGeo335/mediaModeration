import os
import re
from pathlib import Path
from loguru import logger

def preprocessingText(text: str):
    logger.info(f"Начало обработки текста...")

    """1) Транслитерация символов на русский"""
    text = text.lower()

    translit_dict = {
            'a': 'а', 
            'b': 'б', 
            'c': 'с', 
            'd': 'д', 
            'e': 'е', 
            'f': 'ф', 
            'g': 'г',
            'h': 'х', 
            'i': 'и', 
            'j': 'ж', 
            'k': 'к', 
            'l': 'л', 
            'm': 'м', 
            'n': 'н',
            'o': 'о', 
            'p': 'п', 
            'q': 'к', 
            'r': 'р', 
            's': 'с', 
            't': 'т', 
            'u': 'у',
            'v': 'в', 
            'w': 'в', 
            'x': 'х', 
            'y': 'у', 
            'z': 'з'
        }
    
    newText = ""
    for char in text:
        if char in translit_dict:
            newText += translit_dict[char]
        else:
            newText+= char
    text = newText 

    """2)Транслитерация символов похожих на @"""
    text = text.replace('@', 'а')

    """3)Удаление знаков препинания, спец символов и цифр"""
    text = re.sub(r'[^а-яё\s]', '', text)

    """4)Удаление лишних пробеллов"""
    text = re.sub(r'\s+', ' ', text).strip()

    """5) Удаление повторяющихся букв подряд"""
    text = re.sub(r'(.)\1+', r'\1', text)

    logger.info(f"Результат обработки текста: {text}")
    
    return text