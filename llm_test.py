from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModelForSeq2SeqLM
import torch

import LLM
#Импортируем функции для работы
from LLM import translate_en_to_ru, translate_ru_to_en,

# Проверка доступности MPS (Metal для Mac)
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
print(f"Используется устройство: {device}")

# Загрузка модели и токенизатора
model_name = "tanusrich/Mental_Health_Chatbot"
tokenizer = AutoTokenizer.from_pretrained(model_name)

try:
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16 if device.type == "mps" else torch.float32,
        device_map=device if device.type == "mps" else "auto",
        trust_remote_code=True
    )
    print("Модель успешно загружена")
except Exception as e:
    print(f"Ошибка при загрузке модели: {e}")
    model = None

# Загрузка моделей для перевода и их токенизаторов
try:
    # Модель для перевода с русского на английский
    tokenizer_ru_en = AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-ru-en")
    model_ru_en = AutoModelForSeq2SeqLM.from_pretrained(
        "Helsinki-NLP/opus-mt-ru-en",
        torch_dtype=torch.float16 if device.type == "mps" else torch.float32,
        device_map=device
    )
    print("Модель ru-en загружена")

    # Модель для перевода с английского на русский
    tokenizer_en_ru = AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-ru")
    model_en_ru = AutoModelForSeq2SeqLM.from_pretrained(
        "Helsinki-NLP/opus-mt-en-ru",
        torch_dtype=torch.float16 if device.type == "mps" else torch.float32,
        device_map=device
    )
    print("Модель en-ru загружена")

except Exception as e:
    print(f"Ошибка при загрузке моделей перевода: {e}")
    tokenizer_ru_en = model_ru_en = tokenizer_en_ru = model_en_ru = None

# Системный промпт
SYSTEM_PROMPT = """You are Lora, a mental health AI assistant. Rules:
1. Be empathetic and supportive
2. Suggest breathing exercises or yoga
3. NEVER diagnose or prescribe medication
4. Keep responses brief
5. End with: "Remember, I'm an AI assistant, not a therapist"."""

def generate_response(text: str) -> str:
    if model is None:
        return "Извините, модель временно недоступна. Пожалуйста, попробуйте позже."

    prompt = f"{SYSTEM_PROMPT}\n\nUser: {text}\nLora:"

    try:
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=200,
                temperature=0.7, # Это можем менять в пределах 0.5-0.8
                top_p=0.9,
                repetition_penalty=1.1,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id
            )

        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Извлекаем только ответ модели
        if "Lora:" in response:
            response = response.split("Lora:")[-1].strip()

        # Убеждаемся, что есть завершающая фраза на английском
        if not response.endswith('"Remember, I\'m an AI assistant, not a therapist."'):
            response += ' "Remember, I\'m an AI assistant, not a therapist."'

        return response

    except Exception as e:
        print(f"Ошибка генерации: {e}")
        return "Произошла ошибка при обработке запроса. Пожалуйста, попробуйте еще раз."

def main(text):

    en_text = LLM.translate_ru_to_en(text)
    response = generate_response(en_text)
    response_ru = LLM.translate_en_to_ru(response)
    print('Вот ответ нашей модели: \n')
    print(response_ru)

if __name__ == 'main':
    # Сюда введи текст для проверки, вот варианты:
    'Я с трудом сплю и ничего не делаю, но думаю о том, как я бесполезна и как не должна быть здесь я никогда не пробовала или не планировала самоубийство я всегда хотела исправить свои проблемы но я никогда не могу понять как я могу изменить свое чувство никчемности для всех'

    main('Я с трудом сплю и ничего не делаю, но думаю о том, как я бесполезна и как не должна быть здесь я никогда не пробовала или не планировала самоубийство я всегда хотела исправить свои проблемы но я никогда не могу понять как я могу изменить свое чувство никчемности для всех'
)