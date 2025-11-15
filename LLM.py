from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModelForSeq2SeqLM
import torch
import asyncio

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

# Функции для перевода
def translate_ru_to_en(text: str) -> str:
    """Перевод с русского на английский"""
    if model_ru_en is None:
        return text  # Возвращаем оригинал, если модель не загружена

    try:
        inputs = tokenizer_ru_en(text, return_tensors="pt", padding=True, truncation=True, max_length=512).to(device)
        with torch.no_grad():
            translated_tokens = model_ru_en.generate(
                **inputs,
                max_new_tokens=512,
                num_beams=5,
                early_stopping=True
            )
        return tokenizer_ru_en.decode(translated_tokens[0], skip_special_tokens=True)
    except Exception as e:
        print(f"Ошибка перевода ru-en: {e}")
        return text


def translate_en_to_ru(text: str) -> str:
    """Перевод с английского на русский"""
    if model_en_ru is None:
        return text  # Возвращаем оригинал, если модель не загружена

    try:
        inputs = tokenizer_en_ru(text, return_tensors="pt", padding=True, truncation=True, max_length=512).to(device)
        with torch.no_grad():
            translated_tokens = model_en_ru.generate(
                **inputs,
                max_new_tokens=512,
                num_beams=5,
                early_stopping=True
            )
        return tokenizer_en_ru.decode(translated_tokens[0], skip_special_tokens=True)
    except Exception as e:
        print(f"Ошибка перевода en-ru: {e}")
        return text

async def generate_response(text: str) -> str:
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


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Основная функция, обрабатывающая и отвечающая на сообщения пользователя"""
    # Запрос пользователя
    user_text = update.message.text

    if not user_text.strip():
        await update.message.reply_text("Пожалуйста, напишите ваш вопрос.")
        return

    # Отправка статуса "печатает"
    await update.message.chat.send_action(action="typing")

    try:
        # Шаг 1: Переводим русский запрос на английский[citation:8]
        user_text_en = await asyncio.get_event_loop().run_in_executor(
            None, translate_ru_to_en, user_text
        )

        # Шаг 2: Генерируем ответ на английском
        response_en = await asyncio.get_event_loop().run_in_executor(
            None, lambda: asyncio.run(generate_response(user_text_en))
        )

        # Шаг 3: Переводим ответ обратно на русский
        response_ru = await asyncio.get_event_loop().run_in_executor(
            None, translate_en_to_ru, response_en
        )

        # Шаг 4: Отправляем пользователю ответ на русском
        await update.message.reply_text(response_ru)
    except Exception as e:
        print(f"Ошибка: {e}")
        await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я Lora, ИИ-помощник в сфере ментального здоровья. "
        "Готова оказать вам эмоциональную поддержку. Расскажите, что вас беспокоит."
    )


def main():
    # Замени "YOUR_BOT_TOKEN" на токен бота
    application = Application.builder().token("YOUR_BOT_TOKEN").build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен...")
    application.run_polling()


if __name__ == "__main__":
    main()