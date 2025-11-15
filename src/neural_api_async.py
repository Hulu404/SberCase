import requests
import aiohttp
from src.GigaChatDraftBot.config import Config



class AsyncNeuralApi:
    def __init__(self):
        self.api_key = Config.DP_API_KEY
        self.base_url = Config.DP_URL

    def _make_headers(self):
        return {
            "Autorization" : f"Bearer {self.api_key}",
            "Content-Type" : "application/json"
        }

    async def ask_deepseek(self, promt, model=Config.DEFAULT_MODEL):
        # запрос к Deepseek
        data = {
            "model" : model,
            "message" : [{"role":"user", "context" : promt}],
            "max_token" : Config.MAX_TOKENS,
            "temperature" : 0.7
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url,
                    headers=self._make_headers(),
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response.raise_for_status()
                    result = await response.json()
                    return result["choice"][0]["message"]["content"]

        except requests.exceptions.RequestException as _e:
            return f"[INFO] Ошибка API(соединения) {_e}"
        except (KeyError, IndexError) as _ex:
            return "[INFO] Ошибка обработки ответа"