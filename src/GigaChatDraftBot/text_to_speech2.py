import aiohttp
import logging
import asyncio
from yandex_auth import speechkit_auth


class SpeechToTextProcessor:
    """Класс для преобразования речи в текст с предварительной авторизацией"""

    def __init__(self):
        self.auth = speechkit_auth

    async def initialize(self) -> bool:
        """Инициализация и проверка авторизации"""
        try:
            # Предварительная авторизация при запуске
            is_valid = await self.auth.validate_credentials()
            if is_valid:
                logging.info("✅ Yandex SpeechKit авторизация успешна")
                return True
            else:
                logging.error("❌ Ошибка авторизации Yandex SpeechKit")
                return False
        except Exception as e:
            logging.error(f"Ошибка инициализации SpeechKit: {e}")
            return False

    async def speech_to_text(self, audio_data: bytes, language: str = "ru-RU") -> str:
        """
        Преобразует аудио в текст с использованием предварительной авторизации

        Args:
            audio_data: Байты аудио в формате OGG
            language: Язык распознавания

        Returns:
            str: Распознанный текст
        """
        try:
            # Получаем заголовки авторизации
            headers = await self.auth.get_auth_headers(use_iam_token=True)

            # Убираем Content-Type для multipart данных
            headers.pop("Content-Type", None)

            url = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"
            params = {
                "lang": language,
                "folderId": self.auth.folder_id
            }

            # Создаем форму для отправки
            form_data = aiohttp.FormData()
            form_data.add_field('audio', audio_data, filename='audio.ogg', content_type='audio/ogg')

            session = await self.auth.get_session()

            async with session.post(url, headers=headers, params=params, data=form_data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("result", "").strip()
                elif response.status == 401:
                    # Токен устарел, пробуем обновить
                    logging.warning("Токен устарел, обновляем...")
                    headers = await self.auth.get_auth_headers(use_iam_token=True)
                    headers.pop("Content-Type", None)

                    async with session.post(url, headers=headers, params=params, data=form_data) as retry_response:
                        if retry_response.status == 200:
                            result = await retry_response.json()
                            return result.get("result", "").strip()
                        else:
                            error_text = await retry_response.text()
                            logging.error(f"Ошибка после обновления токена: {error_text}")
                            return ""
                else:
                    error_text = await response.text()
                    logging.error(f"Ошибка SpeechKit STT: {error_text}")
                    return ""

        except Exception as e:
            logging.error(f"Ошибка преобразования речи в текст: {e}")
            return ""

    async def close(self):
        """Закрывает соединения"""
        await self.auth.close_session()


# Глобальный экземпляр
speech_processor = SpeechToTextProcessor()