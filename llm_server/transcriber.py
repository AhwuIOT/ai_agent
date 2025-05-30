from faster_whisper import WhisperModel
from .llm_handler import call_lmstudio, LLMRequest
import os
from opencc import OpenCC
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
model = WhisperModel("base", device="cpu", compute_type="int8")
cc = OpenCC('s2t')

def transcribe_audio(file_path):
    print(f"🧠 正在辨識：{file_path}")
    
    segments, _ = model.transcribe(file_path, beam_size=5)
    raw_text = "".join([seg.text for seg in segments])
    print(f"📝 Whisper 原始結果：{raw_text}")
    
    # 建立 LLM 請求
    req = LLMRequest(
        text=raw_text,
        mode="long_speech",  # 要求語句潤飾
        model="lmstudio-community/gemma-3-12B-it-qat-GGUF",  # 可以自由改成你的模型名稱
        temperature=0,
        max_tokens=2048
    )

    polished_text = cc.convert(call_lmstudio(req))
    print(f"✅ 修飾後文字：{polished_text}")

    return polished_text

if __name__ == "__main__":
    transcribe_audio("recordings/record_20250529_173349.wav")