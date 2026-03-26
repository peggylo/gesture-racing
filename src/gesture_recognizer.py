"""
手勢辨識引擎
使用 OpenCV + MediaPipe 辨識手勢，透過 UDP 送出 JSON 給按鍵控制器。
"""

import cv2
import mediapipe as mp
import socket
import json
import os
import time

# === 常數定義 ===

# UDP 設定
UDP_HOST = "127.0.0.1"
UDP_PORT = 9999

# 模型檔案路徑（與本程式同目錄）
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hand_landmarker.task")

# MediaPipe Hand Landmark 索引
WRIST = 0
THUMB_TIP = 4
THUMB_IP = 3
THUMB_MCP = 2
INDEX_TIP = 8
INDEX_PIP = 6
INDEX_MCP = 5
MIDDLE_TIP = 12
MIDDLE_PIP = 10
RING_TIP = 16
RING_PIP = 14
PINKY_TIP = 20
PINKY_PIP = 18
PINKY_MCP = 17

# 閾值
PALM_WIDTH_THRESHOLD = 0.15  # knife vs palm 的手掌寬度閾值
TWO_DIRECTION_THRESHOLD = 0.05  # two 手勢傾斜方向閾值
POINT_DIRECTION_THRESHOLD = 0.04  # point 左右方向閾值


# === 手指伸直判斷 ===

def is_thumb_extended(landmarks):
    """判斷拇指是否伸直：指尖離根部的距離 > IP 關節離根部的距離"""
    return (abs(landmarks[THUMB_TIP].x - landmarks[THUMB_MCP].x) >
            abs(landmarks[THUMB_IP].x - landmarks[THUMB_MCP].x))


def is_finger_extended(landmarks, tip, pip_joint):
    """判斷四指（食指～小指）是否伸直：指尖 y < PIP 關節 y"""
    return landmarks[tip].y < landmarks[pip_joint].y


def get_extended_fingers(landmarks):
    """回傳五根手指的伸直狀態 [thumb, index, middle, ring, pinky]"""
    return [
        is_thumb_extended(landmarks),
        is_finger_extended(landmarks, INDEX_TIP, INDEX_PIP),
        is_finger_extended(landmarks, MIDDLE_TIP, MIDDLE_PIP),
        is_finger_extended(landmarks, RING_TIP, RING_PIP),
        is_finger_extended(landmarks, PINKY_TIP, PINKY_PIP),
    ]


# === 手掌寬度 ===

def get_palm_width(landmarks):
    """計算食指 MCP 與小指 MCP 的 x 軸距離，用來區分 palm 與 knife"""
    return abs(landmarks[INDEX_MCP].x - landmarks[PINKY_MCP].x)


# === 方向判斷 ===

def classify_point_direction(landmarks):
    """
    判斷 point（比 1）的方向。
    用食指指尖相對 MCP 的向量判斷。
    """
    dx = landmarks[INDEX_TIP].x - landmarks[INDEX_MCP].x

    if dx > POINT_DIRECTION_THRESHOLD:
        return "right"
    elif dx < -POINT_DIRECTION_THRESHOLD:
        return "left"
    else:
        return "up"


def classify_two_direction(landmarks):
    """
    判斷 two（比 2）的傾斜方向。
    用食指 MCP 相對手腕的 x 偏移判斷。
    """
    dx = landmarks[INDEX_MCP].x - landmarks[WRIST].x

    if dx < -TWO_DIRECTION_THRESHOLD:
        return "left"
    elif dx > TWO_DIRECTION_THRESHOLD:
        return "right"
    else:
        return "null"


# === 手勢分類 ===

def classify_gesture(landmarks):
    """
    根據手部關節點座標分類手勢。
    回傳 (gesture, direction)。
    """
    fingers = get_extended_fingers(landmarks)
    # fingers = [thumb, index, middle, ring, pinky]

    # 握拳：四指（不含拇指）都沒伸直 → 煞車
    if not any(fingers[1:]):
        return ("knife", "null")

    # 四指（不含拇指）全伸 → palm（待機）
    if all(fingers[1:]):
        return ("palm", "null")

    # 只有食指 + 中指伸直
    if fingers[1] and fingers[2] and not fingers[3] and not fingers[4]:
        direction = classify_two_direction(landmarks)
        return ("two", direction)

    # 只有食指伸直
    if fingers[1] and not fingers[2] and not fingers[3] and not fingers[4]:
        direction = classify_point_direction(landmarks)
        return ("point", direction)

    # 其他未定義手勢 → 待機
    return ("palm", "null")


# === UDP 發送 ===

def send_udp(sock, gesture, direction):
    """透過 UDP 送出手勢 JSON"""
    data = json.dumps({"gesture": gesture, "direction": direction})
    sock.sendto(data.encode(), (UDP_HOST, UDP_PORT))


# === 主程式 ===

def main():
    # 初始化 MediaPipe HandLandmarker（新版 Task API）
    base_options = mp.tasks.BaseOptions(model_asset_path=MODEL_PATH)
    options = mp.tasks.vision.HandLandmarkerOptions(
        base_options=base_options,
        running_mode=mp.tasks.vision.RunningMode.VIDEO,
        num_hands=1,
        min_hand_detection_confidence=0.7,
        min_tracking_confidence=0.5,
    )
    landmarker = mp.tasks.vision.HandLandmarker.create_from_options(options)

    # 繪製用的常數
    hand_connections = mp.tasks.vision.HandLandmarksConnections.HAND_CONNECTIONS
    draw_landmarks = mp.tasks.vision.drawing_utils.draw_landmarks

    # 初始化攝影機
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("錯誤：無法開啟攝影機")
        return

    # 初始化 UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print("手勢辨識引擎已啟動，按 q 離開")

    frame_timestamp_ms = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 水平翻轉（鏡像），讓左右方向與使用者直覺一致
        frame = cv2.flip(frame, 1)

        # 轉 RGB，建立 MediaPipe Image
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # 遞增 timestamp（VIDEO 模式要求 timestamp 嚴格遞增）
        frame_timestamp_ms += 33  # 約 30 fps

        # 偵測手部
        result = landmarker.detect_for_video(mp_image, frame_timestamp_ms)

        gesture = "none"
        direction = "null"

        if result.hand_landmarks:
            landmarks = result.hand_landmarks[0]

            # 辨識手勢
            gesture, direction = classify_gesture(landmarks)

            # 在畫面上繪製手部關節點
            draw_landmarks(frame, landmarks, hand_connections)

        # 顯示手勢資訊
        text = f"gesture: {gesture}, direction: {direction}"
        cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                    (0, 255, 0), 2)

        # 送出 UDP
        send_udp(sock, gesture, direction)

        # 顯示預覽
        cv2.imshow("Gesture Recognizer", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # 清理資源
    cap.release()
    cv2.destroyAllWindows()
    sock.close()
    landmarker.close()
    print("手勢辨識引擎已關閉")


if __name__ == "__main__":
    main()
