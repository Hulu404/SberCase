from src.GigaChatDraftBot.config import TOKEN
from config import AUTH_KEY
import logging
from test_func import *

token = test_func.get_gigachat_token(AUTH_KEY)

Prompt= ... # Сюда впишите ваш запрос

answer = test_func.response_gigachat(Prompt, token=token)
print(f'Ваш ответ:\n{answer}')
