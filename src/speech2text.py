from faster_whisper import WhisperModel
import speech_recognition as sr
# 初始化 Faster-Whisper 模型
model = WhisperModel("base", device="cpu", compute_type="int8")  

# 使用 Whisper 模型轉換文字
def transcribe_audio(file_path):
    print("🧠 開始語音辨識...")
    segments, _ = model.transcribe(file_path, beam_size=5)
    full_text = "".join([seg.text for seg in segments])
    # print("📝 原始輸出：", full_text)
    return full_text



def instruct_speech_to_text(file_path):
    # 建立辨識器與麥克風來源
    
    recognizer = sr.Recognizer()

    with sr.AudioFile(file_path) as source:
        print("🔊 載入音訊中...")
        audio = recognizer.record(source)

    print("🧠 開始語音辨識...")
    try:
        text = recognizer.recognize_google(audio, language="zh-TW")
        print("✅ 辨識結果：", text)
        return text
    except sr.UnknownValueError:
        print("❌ 無法辨識語音")
        return ""
    except sr.RequestError as e:
        print(f"❌ 語音 API 發生錯誤：{e}")
        return ""