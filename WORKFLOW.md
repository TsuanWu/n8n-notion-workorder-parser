# 1006 工作流程與依賴

## 主流程

每小時排程 → 兩轮處理 → 查詢 PDF 補救候選或待辨識派工單 → 下載 PDF → `/convert` → Gemini → 解析 JSON → `/map-personnel` → 日期/信心/人員檢查 → 寫入工項、必要確認備註及屬性。

PDF 補救包含實際 Notion 寫入與封存動作。匯入範本預設停用；測試主流程應使用已授權的測試資料，確認結果後才啟用正式排程。

## 人員 CSV 分支

手動匯出人員名單 → 取得 Notion Members（讀取指定頁面 blocks）→ 整理 CSV 欄位 → 依 ID 取得 Notion 帳號 → 補齊帳號名稱 → 產生 CSV 檔案。

來源頁面需有標題「公司所有人聯絡資訊」，下方表格包含「人員」「Notion帳號」「信箱」。帳號欄需是真實 user mention。User API 回傳缺漏、重複或 Anonymous 名稱時會停止匯出。

CSV 欄位為 `Name,canonical_name,aliases,Notion user ID`。目前服務將 `aliases` 視為 Email，不是以 `|` 分隔的別名清單。請勿套用舊版文件中不同欄位的 CSV。
本專案只提供空標頭 `personnel-map.example.csv`；真實人員資料不提交。
CSV 匯出為 n8n binary 結果，不會自動覆寫主機上的 CSV；需人工核對並更新實際掛載檔案。

## 外部依賴

- n8n Notion credential：資料庫、頁面與使用者資訊讀取，以及主流程寫入所需權限。
- n8n Google Gemini credential：由模型節點使用，未隨工作流程範本提供。
- PDF API：`/convert`（POST，PDF binary）、`/map-personnel`（POST，people_names 陣列）、`/health`（GET）。
- PDF 程式使用暫存檔擷取文字，完成後刪除；不是全程只在記憶體處理。
- PDF 服務讀取 `/app/personnel-map.csv`；n8n 需能在共同網路解析 `pdf-extractor`。

保留原始 1006 的 API version 與模型設定；本次備份不代表外部 API、模型或實際部署相容性已驗證。
