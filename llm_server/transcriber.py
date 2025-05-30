from faster_whisper import WhisperModel

model = WhisperModel("base", device="cpu", compute_type="int8")

def transcribe_audio(file_path):
    print(f"🧠 正在辨識：{file_path}")
    segments, _ = model.transcribe(file_path, beam_size=5)
    return "".join([seg.text for seg in segments])
