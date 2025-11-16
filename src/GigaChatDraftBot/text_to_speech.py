import aiohttp
import io
import logging
from pydub import AudioSegment
from config import YANDEX_API_KEY  # Добавьте в config.py


class SpeechToText:
    def __init__(self, yandex_api_key: str):
        self.yandex_api_key = yandex_api_key

    async def convert_voice_to_text_yandex(self, voice_data: bytes, language: str = 'ru-RU') -> str:
        """
        Преобразует голосовое сообщение в текст через Yandex SpeechKit

        Args:
            voice_data: Bytes голосового сообщения
            language: Язык распознавания ('ru-RU', 'en-US', etc)

        Returns:
            str: Распознанный текст
        """
        try:
            url = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"
            headers = {
                "Authorization": f"Api-Key {self.yandex_api_key}",
            }
            params = {
                "lang": language,
                "format": "oggopus",  # Формат голосовых сообщений Telegram
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                        url,
                        headers=headers,
                        params=params,
                        data=voice_data
                ) as response:

                    if response.status == 200:
                        result = await response.json()
                        return result.get("result", "")
                    else:
                        error_text = await response.text()
                        logging.error(f"Yandex STT error: {error_text}")
                        return ""

        except Exception as e:
            logging.error(f"Ошибка распознавания речи: {e}")
            return ""


# Создаем экземпляр
stt = SpeechToText(YANDEX_API_KEY)


# Асинхронная функция для использования
async def voice_to_text(voice_data: bytes) -> str:
    return await stt.convert_voice_to_text_yandex(voice_data)

