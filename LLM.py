from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from transformers import AutoTokenizer, AutoModelForCausalLM
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

SYSTEM_PROMPT = """Ты – Lora, ИИ-помощник в сфере ментального здоровья. Оказывай эмоциональную поддержку и предлагай практические стратегии преодоления трудностей. Ключевые правила:
- Отвечай на языке пользователя
- Начинай с сочувствия и поддержки
- Поощряй социальные связи
- НЕ ставь диагнозы и не назначай лекарства
- Заканчивай каждый ответ фразой: «Помните, я ИИ-помощник, а не психотерапевт»
- Ответы должны быть поддерживающими, но краткими."""


async def generate_response(text: str) -> str:
    if model is None:
        return "Извините, модель временно недоступна. Пожалуйста, попробуйте позже."

    prompt = f"{SYSTEM_PROMPT}\n\nПользователь: {text}\nLora:"

    try:
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=200,
                temperature=0.7,
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

        # Убеждаемся, что есть завершающая фраза
        if not response.endswith("«Помните, я ИИ-помощник, а не психотерапевт»"):
            response += " «Помните, я ИИ-помощник, а не психотерапевт»"

        return response

    except Exception as e:
        print(f"Ошибка генерации: {e}")
        return "Произошла ошибка при обработке запроса. Пожалуйста, попробуйте еще раз."


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    if not user_text.strip():
        await update.message.reply_text("Пожалуйста, напишите ваш вопрос.")
        return

    # Отправка статуса "печатает"
    await update.message.chat.send_action(action="typing")

    try:
        # Запускаем генерацию в отдельном потоке чтобы не блокировать бота
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: asyncio.run(generate_response(user_text))
        )
        await update.message.reply_text(response)
    except Exception as e:
        print(f"Ошибка: {e}")
        await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я Lora, ИИ-помощник в сфере ментального здоровья. "
        "Готова оказать вам эмоциональную поддержку. Расскажите, что вас беспокоит."
    )


def main():
    # Замените "YOUR_BOT_TOKEN" на реальный токен вашего бота
    application = Application.builder().token("YOUR_BOT_TOKEN").build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен...")
    application.run_polling()


if __name__ == "__main__":
    main()