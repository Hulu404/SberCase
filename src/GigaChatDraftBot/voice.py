import os
from gtts import gTTS
from pydub import AudioSegment

tts = gTTS("Привет! Сегодня солнечно!", lang="ru")
tts.save("test.mp3")
file_way = os.path.realpath("test.mp3")

