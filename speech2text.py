from faster_whisper import WhisperModel
# 初始化 Faster-Whisper 模型
model = WhisperModel("base", device="cpu", compute_type="int8")  

# 使用 Whisper 模型轉換文字
def transcribe_audio(file_path):
    print("🧠 開始語音辨識...")
    segments, _ = model.transcribe(file_path, beam_size=5)
    full_text = "".join([seg.text for seg in segments])
    # print("📝 原始輸出：", full_text)
    return full_text