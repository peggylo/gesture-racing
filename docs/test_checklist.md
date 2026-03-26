# 測試清單

## Phase 2：單元測試

### 程式 A：手勢辨識引擎

- [x] 執行 `python3 gesture_recognizer.py`，攝影機預覽正常、手部關節點有繪製
- [x] 比 1 食指朝上 → 顯示 `point, up`
- [x] 比 1 食指指左 → 顯示 `point, left`
- [x] 比 1 食指指右 → 顯示 `point, right`
- [x] 握拳 → 顯示 `fist, null`
- [x] 比 2 + 手掌左傾 → 顯示 `two, left`
- [x] 比 2 + 手掌右傾 → 顯示 `two, right`
- [x] 掌心正面朝鏡頭 → 顯示 `palm, null`
- [x] 沒有手入鏡 → 顯示 `none, null`
- [x] 用 UDP 監聽確認有收到格式正確的 JSON 封包

### 程式 B：按鍵控制器

- [x] macOS 輔助使用權限已授權
- [x] 執行 `python3 key_controller.py`，顯示啟動訊息
- [x] 送測試 UDP 封包，對應按鍵有正確觸發（開文字編輯器觀察）
- [x] 送 palm/none 封包，所有按鍵正確放開
- [x] Ctrl+C 退出後不卡鍵

## Phase 3：整合測試

- [x] 同時執行程式 A + B，無報錯
- [x] 開啟 HexGL，比 1 朝上 → 賽車前進
- [x] 比 1 指左/右 → 賽車左轉/右轉
- [x] 握拳 → 賽車煞車
- [x] 比 2 + 傾斜 → 賽車飄移
- [x] 掌心朝鏡頭 → 賽車停止動作
- [x] 手勢切換反應流暢、長時間操作穩定
