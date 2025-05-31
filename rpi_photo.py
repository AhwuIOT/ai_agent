import subprocess
from datetime import datetime
import os

def capture_image_from_ffmpeg(device_path="/dev/video0", save_dir="images"):
    os.makedirs(save_dir, exist_ok=True)
    filename = datetime.now().strftime("%Y%m%d_%H%M%S") + ".jpg"
    filepath = os.path.join(save_dir, filename)

    cmd = [
        "ffmpeg", "-y",
        "-f", "v4l2",
        "-input_format", "mjpeg",           
        "-video_size", "1280x960",          
        "-i", device_path,
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
    
    capture_image_from_ffmpeg(device_path="/dev/video0")
