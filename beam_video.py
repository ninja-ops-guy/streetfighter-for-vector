import mss
import cv2
import numpy as np
import requests
import time
import win32gui
import win32con
import sys
import anki_vector
from anki_vector.util import degrees
from PIL import Image
import io
import subprocess
import os
from flask import Flask

# CONFIGURE THESE
WIREPOD_IP = "192.168.1.8"  
WIREPOD_PORT = 8080
# MONITOR_REGION will be set dynamically
FRAME_WIDTH = 184
FRAME_HEIGHT = 96
FPS = 5

# Find the window with 'Street Fighter' in the title
WINDOW_TITLE_KEYWORD = "Fightcade FBNeo"
#CHANGE THIS TOO. HAS TO BE PATH TO YOUR EMULATOR. I USED FIGHTCADE TO GET THIS UP AND RUNNING.
EMULATOR_PATH = r"YOUR\PATH\TO\Fightcade\emulator\fbneo\fcadefbneo.exe"
ROM_NAME = "sfiii3nr1"

# Set working directory to emulator folder (important for some emulators)
EMULATOR_DIR = os.path.dirname(EMULATOR_PATH)

def find_window_rect_by_title(keyword):
    def callback(hwnd, rects):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if keyword.lower() in title.lower():
                rects.append(win32gui.GetWindowRect(hwnd))
        return True
    rects = []
    win32gui.EnumWindows(callback, rects)
    return rects[0] if rects else None

# Launch emulator first
BATCH_PATH = os.path.join(os.path.dirname(__file__), "launch_emulator.bat")
subprocess.Popen([BATCH_PATH])
print("Batch file executed, emulator should launch!")
time.sleep(5)  # Wait for emulator to open

rect = find_window_rect_by_title(WINDOW_TITLE_KEYWORD)
if rect:
    left, top, right, bottom = rect
    width = right - left
    height = bottom - top
    MONITOR_REGION = {"top": top, "left": left, "width": width, "height": height}
    print(f"Found window '{WINDOW_TITLE_KEYWORD}': {MONITOR_REGION}")
    # Warn if not close to expected sizes
    if not ((abs(width - 298) <= 10 and abs(height - 224) <= 10) or (abs(width - 384) <= 10 and abs(height - 224) <= 10)):
        print(f"Warning: Window size {width}x{height} is not close to 298x224 or 384x224!")
else:
    print(f"Window with title containing '{WINDOW_TITLE_KEYWORD}' not found.")
    sys.exit(1)

EXPECTED_SRC_WIDTH = 384
EXPECTED_SRC_HEIGHT = 224

def send_frame_to_vector(img):
    _, buf = cv2.imencode('.png', img)
    files = {'image': ('frame.png', buf.tobytes(), 'image/png')}
    try:
        r = requests.post(
            f"http://{WIREPOD_IP}:{WIREPOD_PORT}/vector/display_image",
            files=files,
            timeout=2
        )
        print("Sent frame:", r.status_code)
    except Exception as e:
        print("Error sending frame:", e)

with anki_vector.Robot() as robot:
    print(dir(robot.screen))

def pil_to_rgb565_bytes(pil_img):
    pil_img = pil_img.resize((184, 96)).convert("RGB")
    arr = np.array(pil_img)
    r = (arr[..., 0] >> 3).astype(np.uint16)
    g = (arr[..., 1] >> 2).astype(np.uint16)
    b = (arr[..., 2] >> 3).astype(np.uint16)
    rgb565 = (r << 11) | (g << 5) | b
    return rgb565.flatten().tobytes()

def prepare_vector_image(frame):
    h, w = frame.shape[:2]
    target_aspect = 184 / 96
    current_aspect = w / h
    if current_aspect > target_aspect:
        new_w = int(h * target_aspect)
        x0 = (w - new_w) // 2
        frame = frame[:, x0:x0+new_w]
    elif current_aspect < target_aspect:
        new_h = int(w / target_aspect)
        y0 = (h - new_h) // 2
        frame = frame[y0:y0+new_h, :]
    frame = cv2.resize(frame, (184, 96))
    pil_img = Image.fromarray(frame).convert("RGB")
    print("Prepared image size:", pil_img.size)
    print("Mean pixel value:", np.array(pil_img).mean())
    return pil_img

with anki_vector.Robot() as robot:
    robot.behavior.set_head_angle(degrees(45.0))
    robot.behavior.set_lift_height(0.0)
    robot.behavior.drive_off_charger()
    with mss.mss() as sct:
        while True:
            sct_img = sct.grab(MONITOR_REGION)
            frame = np.array(sct_img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)
            pil_image = prepare_vector_image(frame)
            print("Prepared image size:", pil_image.size)
            print("Mean pixel value:", np.array(pil_image).mean())
            rgb565_bytes = pil_to_rgb565_bytes(pil_image)
            print("RGB565 bytes length:", len(rgb565_bytes))
            robot.screen.set_screen_with_image_data(rgb565_bytes, duration_sec=2)
            time.sleep(1.0 / FPS)

app = Flask(__name__)

@app.route('/start_game', methods=['POST'])
def start_game():
    # Path to your batch file or directly to your capture script
    BATCH_PATH = os.path.join(os.path.dirname(__file__), "launch_emulator.bat")
    subprocess.Popen([BATCH_PATH])
    return "Game started!", 200

if __name__ == '__main__':

    app.run(port=5005)
