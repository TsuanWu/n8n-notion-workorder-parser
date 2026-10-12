# Notion 派工單自動整理 — 1006

目前範本為 `workflows/Notion_派工單整理_1006.template.json`，取自使用者指定的 1006 匯出檔，共 39 個節點。保留原有流程連線、判讀邏輯與人員 CSV 匯出分支；不是從 live n8n 重新匯出的資料庫備份。

## 功能

- 每小時觸發，建立兩輪處理項目；各輪查詢一筆待辨識派工單。
- PDF 文字擷取使用 `http://pdf-extractor:8000/convert`。
- 人員名稱對照使用 `http://pdf-extractor:8000/map-personnel`。
- Gemini 標題規則以原始 PDF 檔名為準；低信心或人員對照未通過時，標示「內容待確認」並追加原因。
- 通過檢查後依台灣日期判定：後天起 `Not started`、今天或明天 `In progress`、過去日期 `Done`。
- PDF 補救分支會重新上傳、寫入 Files property、驗證後封存原 PDF block。
- 手動人員 CSV 分支讀取 Notion 表格，依 user ID 查詢帳號名稱，再輸出 CSV。

## 公開範本與本機備份

本 Repository 是可分享的程式與設定範本，不儲存完整 n8n 備份。
範本已移除 credential ID/name、Notion 資料庫/頁面 ID、快取資源名稱/網址及執行個體 metadata；重新產生內部 ID，清空 pinData/tags，設為 `active: false`。
原始匯出檔、人員 CSV、資料庫、Volume、加密金鑰、Token 與 .env 只留本機備份，不提交 GitHub。本機備份可以不加密，但不應放入 Git 工作目錄或納入提交。

## 匯入設定

1. 匯入上述 template JSON，保持停用。這不是匯入後立即可執行的完整備份。
2. 「取得頁面內 PDF 候選」與「取得待辨識派工單1」改填實際派工資料庫 ID。
3. 「取得 Notion Members」改填人員資料頁面 ID。此節點實際讀取 blocks，不是列出全工作區成員。
4. 所有 Notion 節點與使用 `notionApi` 的 HTTP 節點重新選擇有權限的 Notion credential。
5. 「Gemini 模型1」重新選擇 Google Gemini credential。原始模型名稱保留，須於目的端確認可用；只填 .env 不會自動建立這個 credential。
6. 使用真實人員 CSV，確認兩個服務位於能互相解析名稱的 Docker 網路，再測試。

## 已有 n8n 的桌機

優先參照 [MIGRATION.md](MIGRATION.md)，使用 `compose.pdf-only.yaml` 規劃 PDF 服務。此檔不建立 n8n，也不掛載 `n8n_data`；需要在 .env 設定 `PERSONNEL_MAP_PATH`。既有 n8n 的網路連接需另外確認與安排。

根目錄 `docker-compose.yml` 與 n8n Dockerfile 保留作舊版完整部署參考。它會建立名為 n8n 的容器，Volume 名稱可能带 Compose 專案前綴；已有 n8n 的電腦不要直接照舊版方式啟動。現有 Images 先比對 ID/digest，再決定是否重用。

## 驗證狀態

這次更新只驗證 JSON、連線完整性、程式碼保留與靜態敏感資料檢查；沒有啟動容器、匯入 live n8n、執行工作流程或更動 Notion。完整 Volume 與 credentials 備份尚待可存取 Docker Engine 後另行完成。

流程細節見 [WORKFLOW.md](WORKFLOW.md)。舊 0818 匯出檔不再作為目前版本；歷史仍保留在 Git 紀錄中。
