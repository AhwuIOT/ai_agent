# 🧠 AI Agent Assistant (Windows 版本)

這是一個基於語音與影像輸入的 AI Agent 系統，具備三個主要工具，透過語音自然語意輸入即可觸發功能。整合本地語音辨識、語意理解、影像辨識與雲端上傳能力。

---

## 📌 專案簡介

使用者可直接對系統說話，例如：「播放聲音」、「語音轉文字」、「現場人數」，系統會自動判斷需求並執行對應動作。

### ✅ 三大工具功能：

| 功能名稱      | 語意觸發關鍵字          | 執行說明                       |
| --------- | ---------------- | -------------------------- |
| 1. 播放聲音   | 播放聲音、喇叭發聲、嗶一下等   | 播放預設提示音 `audio/beep.wav`   |
| 2. 語音轉文字  | 語音轉文字、STT、語音輸入等  | 錄音後轉文字，並將音檔 + 文字上傳至 AWS S3 |
| 3. 鏡頭人數辨識 | 鏡頭中人數、現場人數、拍照辨識等 | 使用攝影機拍照並使用影像模型辨識畫面中人數      |

---

## 🧠 所使用的 AI Service

* **語意理解 (LLM)：**

  * 使用者本地端部署 LM Studio，並使用Google的Gemma3模型（`lmstudio-community/gemma-3-12B-it-qat-GGUF`）
  * API Endpoint: `http://127.0.0.1:1234/v1/chat/completions`

* **語音轉文字 (STT)：**

  * 使用 `faster-whisper` Python 套件，模型為 `"base"`，運行於 CPU `int8` 模式

* **影像分析 (Vision)：**

  * 使用者本地端部署 LM Studio，並使用 HuggingFace 上的輕量型IBM Granite模型(`ibm-granite_granite-vision-3.2-2b`) 
    * 將圖片轉為base64後，透過 API傳送至AI模型，並查詢人數，回傳純數字
    * API Endpoint: `http://127.0.0.1:1234/v1/chat/completions`

---

## 🖥️ 本版本執行環境
- 軟體
    * 作業系統：Windows 11 (x64)
    * Python 版本：3.10+
    * 必須安裝：
        * ffmpeg（可執行於命令列）
        * USB 攝影機（如：Logitech C310）
        * LMStudio及相關模型
- 硬體
    * 處理器：i7-14700
    * GPU：Nvidia super 4080 16GB
    * RAM：64GB
---

## 📁 專案結構

```
project_root/
|   main.py                 # 語音主控流程，整合三個工具
|   README.md
|   requirements.txt
+---audio
|       beep.wav            # 提示音檔
+---images                  # 拍照圖片暫存資料夾
+---recordings              # 錄音與文字儲存資料夾
+---src
|   |   capture_photo.py    # 使用 ffmpeg 拍照
|   |   count_people.py     # 拍照後辨識人數
|   |   data_storage.py     # 錄音 + 上傳至 AWS + 文字生成流程
|   |   llm_handler.py      # 語意分析與圖片模型 API 整合
|   |   record.py           # 播放聲音、簡易錄音模組
|   |   speech2text.py      # 使用 Faster-Whisper 轉換語音文字
|___|   __init__.py

```

---

## 📦 安裝套件

```bash
pip install -r requirements.txt
```

必要套件如下：

```txt
sounddevice
scipy
python-dotenv
boto3
faster-whisper
requests
playsound
opencc-python-reimplemented
```

---

## ⚙️ .env 設定（自行設定，記得添加於.gitignore中）

```env
AWS_ACCESS_KEY_ID=""
AWS_SECRET_ACCESS_KEY=""
AWS_REGION="ap-northeast-1"
S3_BUCKET_NAME=""
CAMERA_NAME="USB2.0 PC CAMERA"
```

---

## 🧪 操作指引（使用者流程）

1. 📦 安裝套件並設定 .env
2. 確保你已安裝好所有依賴套件與 ffmpeg
3. 填寫 .env 中的 AWS 與攝影機參數
4. 🧠 開啟 LM Studio 
5. 載入 Gemma3 及 IBM Granite模型 並啟動 API 伺服器
6. ▶️ 啟動系統`python main.py`
7. 出現提示訊息後，按下`Enter`錄音
8. 錄音完成後，系統會自動語意分類並執行對應工具
9. 🗣️ 語音範例
10. 「播放聲音」👉 喇叭發聲

    「語音轉文字」👉 按下`c`錄音 + 上傳 S3

    「鏡頭中人數」👉 拍照 + 回傳人數

11. 🔚 結束程式`可隨時按下 Ctrl+C 結束程式`

---

## ▶️ 執行方式

```bash
python main.py
```

啟動後會等待你語音輸入指令。

---


## ⚠️ 注意事項

- 🎤 麥克風裝置：系統會自動使用作業系統預設麥克風。若預設裝置無法正常錄音，請至音效設定確認。

- 📷 攝影機名稱必須正確：請在 .env 檔中設定 CAMERA_NAME，可透過 ffmpeg -list_devices true -f dshow -i dummy 查詢可用裝置。

- 🧠 本地 LLM API 須先啟動：請先開啟 LM Studio 並確認其模型部署與 API 服務正常運行。

- ☁️ S3 權限需開啟寫入權限：請確認 .env 中的金鑰與 bucket 有上傳權限。

## 💡 下一步
1. 移植RaspberryPi
2. 使用Gradio製作介面
3. 多用戶高併發服務設計