# Notion 派工單自動整理 - V2

以 Docker Compose 自託管 n8n 與本機 PDF 擷取服務，將 Notion 資料庫中的派工單 PDF 自動辨識、整理工項並回填頁面屬性。

## 功能

- 每小時執行，最多處理兩輪；每輪只取最舊的一筆「尚未辨識」資料。
- 正常流程讀取「派工單」Files property 的 PDF，擷取文字後交由 Gemini 解析。
- 補救流程會檢查「派工單」property 為空的頁面：只有頁面內容嚴格符合「一份 PDF、沒有其他實質內容」時，才會將 PDF 重新上傳至 Files property；確認寫入成功後封存頁面內原始 PDF block。
- Gemini 只將「出勤人員清單」中的實際出勤人員寫入 People property，不納入申請人、PM、填單人、審核人或聯絡人。
- 已對照到 Notion User ID 的人員都可回填，不限制 @jetseaai.com 網域；Notion guest／實習生亦可使用。
- 工項會寫入頁面中的「工項：」標題下方；沒有模板時自動建立「工項／成果回報／回報文件」區段。

## 「內容待確認」規則

下列任一情況會將 Status 設為「內容待確認」：

- Gemini 信心分數低於 80。
- 人員名稱無法完整對照到 Notion User ID。
- 日期、起訖時間或執行時間不明確、缺漏或矛盾。
- 工項無法可靠整理，或內容模糊、缺漏或矛盾。
- 工項提到的執行／負責人員（排除申請相關角色）未列在出勤人員清單。
- 出勤人員清單或其他重要欄位不明確。

Gemini 會將具體原因寫入 review_reason，供後續追加至 Notion 頁面底部的管理者檢查區。

## PDF 補救流程與 binary 資料

Notion File Upload 需要同時使用 PDF binary 與 Notion File Upload ID。建立 Upload ID 的 HTTP Request 節點會只輸出 API 回應，因此流程以 Merge 節點依位置合併：

1. 「下載頁面內 PDF」提供 binary 欄位 pdf。
2. 「建立 Notion 檔案上傳」提供 Upload ID。
3. Merge 合併兩者後，「上傳 PDF 至 Notion」以 multipart/form-data 傳送 pdf。
4. 寫入「派工單」Files property、重新讀取驗證成功後，才封存原 PDF block。

## 專案內容

- docker-compose.yml：n8n 與 pdf-extractor 服務，僅綁定 127.0.0.1:5678。
- pdf-extractor/：本機 PDF 文字擷取與人員名稱對照服務。
- personnel-map.csv：人員別名、Email 與 Notion User ID 對照表。
- workflows/：n8n 工作流匯出檔；匯出時不可包含 credential。
- .env.example：Gemini API Key 環境變數範本。

## 初次設定

1. 將 .env.example 複製為 .env。
2. 在 .env 填入 GEMINI_API_KEY；不要提交 .env 或任何真實權杖。
3. 確認 Notion connection 已被加入目標資料庫。
4. 在 personnel-map.csv 維護姓名／別名與 Notion User ID；guest 也必須有可用的 Notion User ID 與頁面存取權。
5. 從 n8n 匯出工作流至 workflows/ 前，確認 JSON 未包含 credential 或權杖。

## 啟動與更新

首次建置或修改 Dockerfile／PDF 擷取服務時：

~~~powershell
docker compose up -d --build
~~~

僅修改 Compose 環境變數或重新啟動服務時：

~~~powershell
docker compose up -d
~~~

n8n 使用 named volume n8n_data 保存工作流、credential 與 binary 執行資料。請勿在未備份的情況下刪除該 volume。

## 部署前測試

以 3 至 5 份歷史派工單逐份測試，至少確認：

- 日期、出勤人員、派遣類型與工項正確回填。
- guest／實習生可正常寫入 People property。
- 模糊日期、模糊工項與人員名單矛盾會進入「內容待確認」。
- 直接拖入頁面內容的單一 PDF 可轉移至「派工單」Files property。
- PDF 轉移成功後，原頁面 PDF block 才會被封存。
