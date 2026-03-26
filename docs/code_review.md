# Code Review — 手勢操控賽車專案

## 一、程式碼安全性與效能

### 🔴 安全性問題

**1. UDP 無認證機制**

`key_controller.py` 監聽 `localhost:9999`，接受任何來源的封包，沒有驗證發送者。目前在本機沒問題，但如果未來要讓其他人連線，任何人都能送假封包操控遊戲。

**2. 沒有輸入驗證**

`key_controller.py` 收到 JSON 後直接查表，沒有檢查 gesture/direction 的值是否合法。惡意封包可以送任意字串，雖然目前查表找不到就不動作，但缺乏防禦意識。

**3. pynput 系統層級權限**

pynput 模擬的是整台電腦的鍵盤輸入，不只針對遊戲視窗。如果焦點不在遊戲上，按鍵會送到其他應用程式（例如正在編輯的文件），可能造成非預期操作。

**4. 掛上網的架構根本不適用**

目前架構是「本機攝影機 → 本機 UDP → 本機鍵盤模擬 → 本機瀏覽器」，全部在同一台電腦上。如果要讓其他人遠端玩，這個架構需要根本性的改變：

- 手勢辨識應改用 **MediaPipe JavaScript 版本**，直接在使用者的瀏覽器裡跑
- 遊戲操控應改成直接修改 HexGL 的 JavaScript 程式碼，接收手勢事件，而不是模擬鍵盤
- 不需要 UDP，也不需要 pynput
- 整個專案會變成純前端應用，部署到任何靜態網站即可

### 🟡 效能問題

**1. 每幀都送 UDP，即使手勢沒變**

`gesture_recognizer.py` 每一幀都送封包（約每秒 30 次），即使手勢跟上一幀完全相同。可以加一個「手勢有變化才送」的判斷，減少不必要的傳輸。

**2. timestamp 用固定遞增而非實際時間**

`frame_timestamp_ms += 33` 是假設固定 30fps，但實際攝影機幀率可能波動。應改用 `time.time()` 取得實際時間，避免與 MediaPipe 內部追蹤邏輯產生偏差。

**3. gesture_recognizer 沒有 graceful shutdown**

`key_controller.py` 有 signal handler 處理 Ctrl+C，但 `gesture_recognizer.py` 沒有。雖然按 `q` 可以退出，但如果用 Ctrl+C 中斷，攝影機和 socket 可能沒有正確釋放。

## 二、互動過程回顧

### 🟢 做得好的部分

- **先討論再動手**：在寫程式前充分討論了架構、手勢設計、通訊介面，避免做完才發現方向不對
- **增量測試**：按 Phase 分階段測試，發現問題能快速定位（MediaPipe API 問題、手勢辨識不準確）
- **文件先行**：有 plan.md 和 test_checklist.md 追蹤進度，不會迷路

### 🟡 可以更好的部分

**1. Agent Team 的效益有限**

這個專案的規模其實不需要 agent team。兩支程式加起來不到 350 行，拆成兩個 agent 反而多了溝通成本（通訊介面規格、等待確認、agent 斷線重連）。如果是一個 agent 從頭寫到尾，可能更快。Agent team 適合真正可以大規模平行的任務。

**2. MediaPipe 版本問題應提前確認**

Agent 用了已廢棄的 `mp.solutions` API，測試時才發現。應該在開發前先確認本機 mediapipe 版本和對應 API，避免寫完才重寫。

**3. 手勢可行性應先驗證**

knife（刀手）手勢在 MediaPipe 上辨識困難，最後改成握拳。如果一開始先做一個快速原型測試每種手勢的辨識穩定度，可以避免來回修改。

**4. 終端機指令斷行問題**

用 `&&` 串接的長指令在終端機容易被換行切斷，發生了兩次。應該分開給指令，或提醒使用者確保在同一行貼上。

### 如果要掛上網的建議路線

1. 將 `gesture_recognizer.py` 的邏輯移植到 JavaScript（MediaPipe 有官方 JS SDK）
2. 直接修改 HexGL 的 `ShipControls.js`，新增一個 gesture controller 接收辨識結果
3. 拿掉 `key_controller.py` 和 UDP，全部在瀏覽器內完成
4. 部署為靜態網站（GitHub Pages、Vercel 等）

這樣任何人開瀏覽器、允許攝影機權限就能玩，不需要安裝任何東西。
