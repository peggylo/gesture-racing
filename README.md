# Gesture Racing — 手勢操控賽車遊戲

用手勢操控 HexGL 賽車遊戲。透過攝影機即時辨識手勢，模擬鍵盤輸入控制遊戲。

**本專案為 Claude Code 人機協作開發的實驗專案。目前僅支援本機使用，若要改為線上版本有安全性與架構上的問題需要處理，請務必參考 [Code Review](docs/code_review.md)。**

**本專案可能存在未發現的問題或錯誤，歡迎開 [Issue](https://github.com/peggylo/gesture-racing/issues) 回報或提出改善建議。**

## 架構

```
攝影機 → [手勢辨識引擎] —UDP→ [按鍵控制器] → 鍵盤事件 → HexGL（瀏覽器）
```

## 手勢操作

| 手勢 | 動作 |
|------|------|
| 比 1 食指朝上 | 直走加速 |
| 比 1 食指指左 | 左轉 |
| 比 1 食指指右 | 右轉 |
| 握拳 | 煞車 |
| 比 2 + 左傾 | 左飄移 |
| 比 2 + 右傾 | 右飄移 |
| 掌心朝鏡頭 | 待機 |

## 環境需求

- macOS
- Python 3.10+
- Chrome 瀏覽器

## 安裝

```bash
# 安裝 Python 套件
pip install -r requirements.txt

# 下載手部辨識模型（放在 src/ 目錄下）
wget -O src/hand_landmarker.task https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task

# Clone HexGL 遊戲（獨立專案，不包含在本 repo 中）
git clone https://github.com/BKcore/HexGL.git
```

## 使用方式

1. 啟動 HexGL 遊戲
```bash
cd HexGL && python3 -m http.server 8080
```

2. 啟動按鍵控制器
```bash
python3 src/key_controller.py
```

3. 啟動手勢辨識引擎
```bash
python3 src/gesture_recognizer.py
```

4. 開啟瀏覽器 `http://localhost:8080`，點擊遊戲視窗開始遊玩

**注意：** macOS 需在「系統設定 → 隱私權與安全性」中授權終端機的「輔助使用」及「攝影機」權限。

## 檔案結構

```
├── src/
│   ├── gesture_recognizer.py  # 手勢辨識引擎（MediaPipe + OpenCV）
│   └── key_controller.py      # 按鍵控制器（pynput）
├── docs/
│   ├── plan.md                # 專案規劃
│   ├── test_checklist.md      # 測試清單
│   ├── code_review.md         # Code Review（含已知限制與改進方向）
│   └── learn.md               # 學習筆記
├── requirements.txt           # Python 套件依賴
└── README.md
```

## 通訊介面

兩支程式透過 UDP `localhost:9999` 通訊，封包格式：

```json
{"gesture": "point", "direction": "left"}
```

## 已知限制

本專案目前為本機（localhost）概念驗證，架構上依賴本機 UDP 通訊與系統層級鍵盤模擬，不適用於線上部署。若要讓其他人透過網路遊玩，需要根本性的架構調整。相關分析與建議路線請參考 [Code Review](docs/code_review.md)。

## 製作過程

本專案由人類與 [Claude Code](https://claude.ai/code) 於終端機開發協作完成，包含需求討論、架構設計、程式開發到測試除錯及 Code Review，以下為過程縮時紀錄：

<a href="https://youtu.be/bzPymAd4ZHY">
  <img src="https://img.youtube.com/vi/bzPymAd4ZHY/maxresdefault.jpg" width="50%" alt="製作過程縮時影片">
</a>

🎬 https://youtu.be/bzPymAd4ZHY
