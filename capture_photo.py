import subprocess
from datetime import datetime
import os

def capture_image_from_ffmpeg(camera_name,save_dir="images"):
    os.makedirs(save_dir, exist_ok=True)
    filename = datetime.now().strftime("%Y%m%d_%H%M%S") + ".jpg"
    filepath = os.path.join(save_dir, filename)

    cmd = [
    "ffmpeg", "-y",
    "-f", "dshow",
    "-video_size", "640x480",  # 或其他你知道支援的解析度
    "-i", f"video={camera_name}",
    "-frames:v", "1",
    filepath
]
       
    result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    if result.returncode != 0 or not os.path.exists(filepath):
        print("⚠️ ffmpeg 錯誤訊息：")
        print(result.stderr.decode())
        raise Exception("❌ 拍照失敗")
    
    print(f"✅ 圖片儲存：{filepath}")
    return filepath


if __name__ == "__main__":
    camera_name = os.getenv("CAMERA_NAME", "USB2.0 PC CAMERA")
    print(f"📷 使用攝影機：{camera_name}")
    capture_image_from_ffmpeg(camera_name=camera_name)
