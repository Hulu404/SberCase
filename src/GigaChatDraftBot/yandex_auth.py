
import aiohttp
import json
import logging
import time
from config import YANDEX_API_KEY, YANDEX_FOLDER_ID

class YandexSpeechKitAuth:
    """
    Класс для управления авторизацией в Yandex SpeechKit
    Поддерживает IAM-токены и API-ключи
    """

    def __init__(self, api_key: str = None, folder_id: str = None):
        self.api_key = api_key or YANDEX_API_KEY
        self.folder_id = folder_id or YANDEX_FOLDER_ID
        self.iam_token = None
        self.iam_token_expires = 0
        self._session = None

    async def get_session(self) -> aiohttp.ClientSession:
        """Получает или создает aiohttp сессию"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close_session(self):
        """Закрывает сессию"""
        if self._session and not self._session.closed:
            await self._session.close()

    async def get_iam_token(self) -> str:
        """
        Получает IAM-токен для аутентификации
        Токен действует 12 часов, но мы обновляем через 11
        """
        # Если токен еще действителен
        if self.iam_token and time.time() < self.iam_token_expires:
            return self.iam_token

        logging.info("Получение нового IAM-токена...")

        url = "https://iam.api.cloud.yandex.net/iam/v1/tokens"
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "yandexPassportOauthToken": self.api_key
        }

        session = await self.get_session()

        try:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    self.iam_token = data["iamToken"]
                    # Устанавливаем время истечения (11 часов для надежности)
                    self.iam_token_expires = time.time() + 11 * 3600
                    logging.info("IAM-токен успешно получен")
                    return self.iam_token
                else:
                    error_text = await response.text()
                    logging.error(f"Ошибка получения IAM-токена: {error_text}")
                    raise Exception(f"Failed to get IAM token: {response.status}")
        except Exception as e:
            logging.error(f"Ошибка при получении IAM-токена: {e}")
            raise

    async def validate_credentials(self) -> bool:
        """Проверяет валидность учетных данных"""
        try:
            # Пробуем получить IAM-токен
            token = await self.get_iam_token()
            return bool(token)
        except Exception as e:
            logging.error(f"Невалидные учетные данные: {e}")
            return False

    async def get_auth_headers(self, use_iam_token: bool = True) -> dict:
        """
        Возвращает заголовки для аутентификации

        Args:
            use_iam_token: Использовать IAM-токен (True) или API-ключ (False)
        """
        if use_iam_token:
            token = await self.get_iam_token()
            return {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        else:
            # Используем API-ключ напрямую
            return {
                "Authorization": f"Api-Key {self.api_key}",
                "Content-Type": "application/json"
            }

# Глобальный экземпляр для использования в приложении
speechkit_auth = YandexSpeechKitAuth()