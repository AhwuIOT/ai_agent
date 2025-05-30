import os
import re
import sounddevice as sd
import scipy.io.wavfile as wav
from playsound import playsound
from opencc import OpenCC
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
sound_path = "audio/beep.wav"
cc = OpenCC('s2t')  # 簡轉繁


# 播放音效
def play_sound():
    print("🔊 播放音效中...")
    playsound(sound_path)

# 正規化處理
def normalize(text):
    text = cc.convert(text)
    text = re.sub(r'\s+', '', text)
    text = re.sub(r'[^\w\u4e00-\u9fff]', '', text)
    return text.lower()

# 錄音 5 秒並儲存成 wav 檔
def record_audio(file_path="recordings/record.wav", duration=5, samplerate=16000):
    print("🎙️ 開始錄音...")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()
    wav.write(file_path, samplerate, audio)
    print("✅ 錄音完成：", file_path)
    return file_path
