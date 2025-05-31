from src.record import record_audio, play_sound
from src.speech2text import instruct_speech_to_text
from src.data_storage import tool_speech_to_text
from src.count_people import capture_and_count_people
def main():
    print("🎧 語音助理已啟動，按 Enter 開始一次錄音，Ctrl+C 離開")
    while True:
        try:
            input("\n🔘 按 Enter 錄音...")
            audio_path = record_audio()
            intent = instruct_speech_to_text(audio_path)
        
            print("🧠 語意判斷結果：", intent)

            if intent == "play_sound":
                play_sound()
            elif intent == "record":
                print("🗣️ 偵測到錄音指令，可觸發錄音流程")
                tool_speech_to_text()
            elif intent == "camera":
                print("📸 偵測到鏡頭指令，可執行影像處理流程")
                capture_and_count_people()
            else:
                print("❓ 無法判斷語意")

        except KeyboardInterrupt:
            print("\n👋 已離開語音助理")
            break
        except Exception as e:
            print(f"❌ 發生錯誤：{e}")

if __name__ == "__main__": 
    main()