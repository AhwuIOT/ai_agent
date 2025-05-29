from .llm_handler import match_intent
from .capture_photo import capture_image_from_ffmpeg
def capture_and_count_people():
    file_path = capture_image_from_ffmpeg(camera_name="USB2.0 PC CAMERA", save_dir="images")
    prediction = match_intent(file_path, "count_people")
    print(prediction)

if __name__ == "__main__":
    capture_and_count_people()