"""
按鍵控制器 — 接收 UDP 手勢封包，模擬鍵盤按鍵操控 HexGL 賽車遊戲
"""

import socket
import json
import signal
import sys
from pynput.keyboard import Key, KeyCode, Controller

# UDP 設定
UDP_HOST = "127.0.0.1"
UDP_PORT = 9999
BUFFER_SIZE = 1024

# 鍵盤控制器
keyboard = Controller()

# 手勢對應表：(gesture, direction) → 按鍵
GESTURE_KEY_MAP = {
    ("point", "up"): Key.up,
    ("point", "left"): Key.left,
    ("point", "right"): Key.right,
    ("knife", "null"): Key.down,
    ("two", "left"): KeyCode.from_char("q"),
    ("two", "right"): KeyCode.from_char("e"),
}

# 放開所有鍵的手勢
RELEASE_GESTURES = {"palm", "none"}

# 目前被按住的按鍵集合
pressed_keys = set()


def release_all():
    """放開所有目前被按住的按鍵"""
    for key in list(pressed_keys):
        keyboard.release(key)
    pressed_keys.clear()


def update_keys(target_keys):
    """
    根據目標按鍵集合，差異更新按鍵狀態：
    - 放開不在目標中的舊按鍵
    - 按下目標中尚未按住的新按鍵
    """
    to_release = pressed_keys - target_keys
    to_press = target_keys - pressed_keys

    for key in to_release:
        keyboard.release(key)
        pressed_keys.discard(key)

    for key in to_press:
        keyboard.press(key)
        pressed_keys.add(key)


def get_target_keys(gesture, direction):
    """查表取得目標按鍵集合"""
    if gesture in RELEASE_GESTURES:
        return set()

    # 將 None 轉為字串 "null" 以對應查表
    if direction is None:
        direction = "null"

    key = GESTURE_KEY_MAP.get((gesture, direction))
    if key is not None:
        return {key}

    return set()


def handle_exit(signum, frame):
    """收到中斷訊號時，放開所有按鍵再退出"""
    print("\n正在退出，放開所有按鍵...")
    release_all()
    sys.exit(0)


def main():
    # 註冊訊號處理，確保退出時放開所有按鍵
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    # 建立 UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_HOST, UDP_PORT))

    print(f"按鍵控制器已啟動，監聽 {UDP_HOST}:{UDP_PORT}")
    print("提醒：macOS 需在「系統設定 → 隱私權與安全性 → 輔助使用」授權終端機或 Python")
    print("按 Ctrl+C 退出")

    try:
        while True:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            try:
                msg = json.loads(data.decode("utf-8"))
                gesture = msg.get("gesture", "none")
                direction = msg.get("direction", "null")

                target_keys = get_target_keys(gesture, direction)
                update_keys(target_keys)

            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                print(f"封包解析錯誤：{e}")

    except Exception as e:
        print(f"發生錯誤：{e}")
    finally:
        release_all()
        sock.close()
        print("已關閉連線")


if __name__ == "__main__":
    main()
