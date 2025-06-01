# 🧠 AI Agent Assistant (Raspberry Pi 版本)

這是一個基於語音與影像輸入的 AI Agent 系統，具備三個主要工具，透過語音自然語意輸入即可觸發功能。整合本地錄音、遠端語音辨識與語意理解、影像辨識與雲端上傳能力。

---

## 📌 專案簡介

使用者可直接對系統說話，例如：「播放聲音」、「語音轉文字」、「現場人數」，系統會自動判斷需求並執行對應動作。

### ✅ 三大工具功能：

| 功能名稱      | 語意觸發關鍵字          | 執行說明                               |
| --------- | ---------------- | ---------------------------------- |
| 1. 播放聲音   | 播放聲音、喇叭發聲、嗶一下等   | 播放預設提示音 `audio/beep.wav`           |
| 2. 語音轉文字  | 語音轉文字、STT、語音輸入等  | 錄音後透過網路傳給伺服器辨識，並將音檔 + 文字上傳至 AWS S3 |
| 3. 鏡頭人數辨識 | 鏡頭中人數、現場人數、拍照辨識等 | 使用攝影機拍照並透過伺服器模型辨識畫面中人數             |

---

## 🧠 所使用的 AI 服務（部署於伺服器端）

* **語意理解 (LLM)**：LM Studio + Gemma3 模型（`lmstudio-community/gemma-3-12B-it-qat-GGUF`）

  * API Endpoint 範例：`http://<伺服器 IP>:1234/v1/chat/completions`

* **語音轉文字 (STT)**：Faster-Whisper 模型，部署於伺服器端，以 REST API 提供語音轉文字服務。

* **影像分析 (Vision)**：LM Studio + IBM Granite 模型（`ibm-granite_granite-vision-3.2-2b`），辨識影像中人數

---

## 🖥️ 執行環境

* 軟體（Raspberry Pi 上）

  * 作業系統：Raspberry Pi OS / Debian
  * Python：3.10+
  * 必須安裝：

    * ffmpeg（命令列可執行）
    * USB 攝影機（如：Logitech C310）
    * requests, boto3 等相關 Python 套件

* 硬體（Raspberry Pi）

  * Raspberry Pi 4 或以上
  * USB 麥克風 / 攝影機
  * 建議搭配伺服器執行 Heavy AI 模型

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
|   |   record.py           # 播放聲音、簡易錄音模組
|   |   speech2text.py      # 使用 REST API 傳送至伺服器轉文字
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
requests
playsound
opencc-python-reimplemented
keyboard
```

---

## ⚙️ .env 設定

```env
AWS_ACCESS_KEY_ID=""
AWS_SECRET_ACCESS_KEY=""
AWS_REGION="ap-northeast-1"
S3_BUCKET_NAME=""
API_URL="http://<伺服器 IP>"
```

請將 `<伺服器 IP>` 替換成實際提供 LM Studio 與 STT API 的機器 IP。

---

## 🧪 操作流程

1. 📦 安裝套件並設定 `.env`
2. 確保 Raspberry Pi 能連到伺服器 IP
3. 填寫 `.env` 中 AWS 與 API\_URL 參數
4. ▶️ 啟動系統：`python main.py`
5. 📣 出現提示後按 `Enter` 開始錄音
6. 🧠 系統會自動語意分析並執行對應功能

---

## ▶️ 執行方式

```bash
python main.py
```

---

## ⚠️ 注意事項

* 🎤 麥克風使用 Raspberry Pi 預設裝置，請確認錄音功能正常
* 📷 攝影機可使用 `/dev/video0`，支援 V4L2 且需支援 ffmpeg
* 🧠 所有 LLM 與 Faster-Whisper 模型需先在伺服器上啟動，並確認 API 可用
* 📡 Raspberry Pi 僅作為前端控制節點，將資料透過網路送往伺服器分析

---

## 💡 下一步

1. 整合 Gradio 或 Streamlit 製作簡易網頁介面
2. 自動化部署與監控模組
