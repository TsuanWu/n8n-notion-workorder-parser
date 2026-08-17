# Notion 派工單自動整理 - V1

使用既有的 Notion「派工與成果回報資料庫」。使用者新增派工項目、附上 PDF，並讓預設 Status 為「尚未辨識」。n8n 每小時最多處理兩份。

## V1 流程

1. 查詢 `Status = 尚未辨識` 且 `派工單` 有附件的前兩筆。
2. 下載 PDF 到 n8n binary 欄位 `pdf`。
3. 寫入容器暫存檔，使用 MarkItDown 轉為 Markdown。
4. Markdown 少於 100 個字、轉檔失敗或 PDF 不可讀：不呼叫 Gemini，將 Status 設為「內容待確認」，並在 Notion 頁面末尾寫入原因。
5. Gemini 僅從 Markdown 擷取結構化資料：標題、日期、人員名稱、派遣類型、信心與待確認原因。
6. n8n 以 `person_mapping.csv` 將人名／別名轉為 Email 與 Notion User ID，回填 Name、Date、Person、派遣類型。
7. 成功時 Status 設為 `Not started`；低信心或資料缺漏時設為「內容待確認」並附「AI 辨識檢查」。

V1 不含 OCR。因此掃描型 PDF 通常會進入「內容待確認」，不會浪費 Gemini 額度。

## 專案內容

- `Dockerfile`：自訂 n8n image，內建 Python 3.12 與 `markitdown[pdf]`。
- `docker-compose.yml`：僅綁定 `127.0.0.1:5678`，不開放區網或外網。
- `person_mapping.csv`：人員別名對照範本。`aliases` 使用 `|` 分隔。
- `workflows/notion-dispatch-v1.json`：工作流匯出位置；匯出時不可包含 credential。

## 初次設定

1. 將 `.env.example` 複製為 `.env`。
2. 建立 Gemini API Key，僅填入 `.env` 的 `GEMINI_API_KEY`；不要貼入聊天、Notion 或 Git。
3. 本機開發環境會沿用既有 Docker volume `n8n_data`，因此保留目前的 n8n 加密設定、工作流與 Notion credential。
4. 在公司新主機首次部署時，讓 n8n 建立並持久化自己的加密設定；之後不可刪除該 volume。
5. 完成工作流後，從 n8n 匯出 JSON 到 `workflows/notion-dispatch-v1.json`，確認 JSON 沒有真實權杖再提交 Git。

## 啟動

```powershell
docker compose up -d --build
```

在同一台電腦瀏覽 `http://localhost:5678`。在公司無頭電腦上同樣透過本機或受控遠端桌面管理；不需要 VPN，因為 n8n 不對外提供操作入口。

## 部署前測試

用 3 至 5 份歷史派工單逐份建立測試項目。確認每一項的日期、人員、類型與「內容待確認」訊息後，再發布排程工作流。
