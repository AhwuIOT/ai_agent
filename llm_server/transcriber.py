from faster_whisper import WhisperModel
from .llm_handler import call_lmstudio, LLMRequest
import os
from opencc import OpenCC
from pydub import AudioSegment
import tempfile
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
model = WhisperModel("base", device="auto", compute_type="float16")
cc = OpenCC('s2t')

def transcribe_audio(file_path):
    print(f"🧠 正在辨識：{file_path}")


    # 檢查副檔名，非 wav 則先轉檔
    ext = os.path.splitext(file_path)[-1].lower()
    if ext not in [".wav"]:
        print("🔄 正在轉檔成 wav...")
        audio = AudioSegment.from_file(file_path, format=ext[1:])
        temp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        audio.set_frame_rate(16000).set_channels(1).export(temp_wav.name, format="wav")
        file_path = temp_wav.name
        print(f"🎧 轉檔成功：{file_path}")
    
    segments, _ = model.transcribe(file_path, beam_size=5)
    raw_text = "".join([seg.text for seg in segments])
    print(f"📝 Whisper 原始結果：{raw_text}")
    
    # # 建立 LLM 請求
    # req = LLMRequest(
    #     text=raw_text,
    #     mode="long_speech",  # 要求語句潤飾
    #     model="lmstudio-community/gemma-3-12B-it-qat-GGUF",  # 可以自由改成你的模型名稱
    #     temperature=0,
    #     max_tokens=2048
    # )

    polished_text = cc.convert(raw_text)
    print(f"✅ 修飾後文字：{polished_text}")
    
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"🗑️ 已刪除檔案：{file_path}")
        except Exception as e:
            print(f"⚠️ 刪除失敗：{e}")


    return polished_text



if __name__ == "__main__":
    transcribe_audio("recordings/test.mp3")