
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import os
from dotenv import load_dotenv
import boto3
from datetime import datetime
from .llm_handler import match_intent
import keyboard
from .speech2text import transcribe_audio
# 載入 AWS 設定
load_dotenv()
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
BUCKET_NAME = os.getenv("S3_BUCKET_NAME")



def record_audio(audio_path):
    fs = 16000
    print("📢 按下 c 鍵開始錄音，錄完後再次按下 c 結束錄音...")
    keyboard.wait("c")
    print("🎙️ 錄音中...")

    frames = []

    def callback(indata, frames_count, time_info, status):
        frames.append(indata.copy())

    with sd.InputStream(samplerate=fs, channels=1, callback=callback):
        keyboard.wait("c")

    print("🛑 錄音結束，儲存音檔中...")
    audio_data = np.concatenate(frames, axis=0)
    os.makedirs(os.path.dirname(audio_path), exist_ok=True)
    write(audio_path, fs, audio_data)
    print("📁 音訊儲存於：", audio_path)
    return audio_path

def upload_to_s3(file_path, s3_key):
    session = boto3.session.Session(
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION,
    )
    s3 = session.client("s3")
    s3.upload_file(file_path, BUCKET_NAME, s3_key)
    print(f"☁️ 上傳成功：s3://{BUCKET_NAME}/{s3_key}")

def transcribe_with_faster_whisper(audio_path):
    segments = transcribe_audio(audio_path)
    # text = "".join([seg.text for seg in segments])
    print("📝 轉譯文字：", segments)
    return segments

def tool_speech_to_text():
    filename_base = datetime.now().strftime("record_%Y%m%d_%H%M%S")
    audio_path = f"recordings/{filename_base}.wav"
    txt_path = f"recordings/{filename_base}.txt"

    record_audio(audio_path)
    text = transcribe_with_faster_whisper(audio_path)
    refined_text = match_intent(text, mode="long_speech")
    print("📝 經過LLM後的文字：", refined_text)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(refined_text)

    upload_to_s3(audio_path, f"record/{os.path.basename(audio_path)}")
    upload_to_s3(txt_path, f"record/{os.path.basename(txt_path)}")

if __name__ == "__main__":
    tool_speech_to_text()
