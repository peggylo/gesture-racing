# 手勢操控賽車遊戲 — 專案規劃

## 專案目標

用攝影機捕捉手勢，透過 MediaPipe 辨識，模擬鍵盤輸入來操控 HexGL 賽車遊戲。

## 架構

```
攝影機 → [程式 A: 手勢辨識] —UDP→ [程式 B: 按鍵控制] → macOS 鍵盤事件 → HexGL（瀏覽器）
```

## 遊戲

- HexGL（HTML5/WebGL），MIT License
- 已部署在本地，透過 localhost 啟動
- 需自行 clone：`git clone https://github.com/BKcore/HexGL.git`

## 手勢對應表

| gesture | direction | 手勢描述 | 對應按鍵 |
|---------|-----------|---------|----------|
| `point` | `up` | 比 1，食指朝上 | ↑（直走加速） |
| `point` | `left` | 比 1，食指指左 | ←（左轉） |
| `point` | `right` | 比 1，食指指右 | →（右轉） |
| `fist` | `null` | 握拳 | ↓（煞車） |
| `two` | `left` | 比 2 + 左傾 | Q（左飄移） |
| `two` | `right` | 比 2 + 右傾 | E（右飄移） |
| `palm` | `null` | 掌心朝鏡頭 | 無（待機） |
| `none` | `null` | 沒偵測到手 | 無（無動作） |

## 通訊介面規格

- 協定：UDP
- 位址：`localhost:9999`
- 方向：A 送 → B 收
- 格式：每個封包一行 JSON，例如 `{"gesture": "point", "direction": "left"}`
- 頻率：跟攝影機幀率一致（約 30 fps）

## 程式分工

### 程式 A：手勢辨識引擎

- 技術：Python + OpenCV + MediaPipe
- 職責：讀攝影機、辨識手部 21 個關節點、判斷手勢、透過 UDP 送出 JSON
- 檔案：`src/gesture_recognizer.py`

### 程式 B：按鍵控制器

- 技術：Python + pynput
- 職責：接收 UDP JSON、對應手勢到按鍵、模擬鍵盤事件
- 檔案：`src/key_controller.py`

## 開發步驟

### Phase 0：遊戲部署 ✅ 已完成
- Clone HexGL 到本地
- 確認 localhost 可啟動並正常遊玩
- 確認鍵盤操控正常

### Phase 1：平行開發（Agent Team） ✅ 已完成
- **Agent 1** 開發程式 A（手勢辨識引擎）
- **Agent 2** 開發程式 B（按鍵控制器）
- 兩邊依照通訊介面規格各自開發，互不相依

### Phase 2：單元測試 ✅ 已完成
- 程式 A：確認攝影機讀取正常、MediaPipe 辨識正常、手勢判斷正確、UDP 封包有送出
- 程式 B：確認 UDP 接收正常、JSON 解析正確、按鍵模擬有觸發（需先處理 macOS 輔助使用權限）

### Phase 3：整合測試 ✅ 已完成
- 同時啟動程式 A + 程式 B，確認手勢能正確轉為按鍵
- 開啟 HexGL，實際用手勢操控遊戲
- 調整手勢判斷的靈敏度與閾值

## 注意事項

- macOS 需在「系統設定 → 隱私權 → 輔助使用」授權終端機或 Python，否則模擬按鍵會被擋
- 如 pynput 在 macOS 無法正常運作，備選方案是改用 Quartz 框架直接送鍵盤事件
