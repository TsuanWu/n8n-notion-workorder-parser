# 派工單自動整理工作流

## 目前已完成

| 順序 | n8n 節點 | 用途 | 必要設定 |
| --- | --- | --- | --- |
| 1 | Schedule Trigger | 每小時檢查一次 | Every hour, `:00`；部署時設 `Asia/Taipei` |
| 2 | Get many database pages | 取最多 2 筆待處理派工單 | Status = `尚未辨識`、`派工單` 有附件、Limit = 2 |
| 3 | HTTP Request - 下載 PDF | 直接取得附件 binary | GET `{{ $json.property_派工單[0].url }}`；Response Format = File；Output field = `pdf` |

> Notion 附件網址有時效。測試時請從第 1 或第 2 節點重新執行，不能單獨重跑舊的下載節點。

## 下一段：本機 PDF 擷取

新增一個 HTTP Request 節點，接在「下載 PDF」後方：

| 設定 | 值 |
| --- | --- |
| Method | POST |
| URL | `http://pdf-extractor:8000/extract` |
| Send Body | On |
| Body Content Type | n8n Binary File |
| Input Data Field Name | `pdf` |

此節點會收到 `{ text, method, pages, warnings }`。PDF 只在 Docker 內部網路流轉，不需要寫入磁碟。

## Gemini 判讀

在本機 PDF 擷取後新增 Gemini HTTP Request。完成 API key credential 後再設定，請求內容要求回傳嚴格 JSON：

```json
{
  "title": "派工單名稱",
  "date_start": "YYYY-MM-DD 或 null",
  "date_end": "YYYY-MM-DD 或 null",
  "dispatch_type": "既有選項名稱或 null",
  "people_names": ["文件中的姓名"],
  "confidence": 0.0,
  "issues": ["缺失、矛盾或無法判斷的原因"]
}
```

規則：不得猜測；任一必填欄位不可靠、無法匹配人員或 `confidence < 0.8` 時，標記為 `內容待確認`。

## 人員對照

準備 `personnel-map.csv` 後，加入「Extract from File（CSV）」與 Code 節點，將 AI 識別的中文姓名／別名轉成 Notion User ID。

CSV 欄位：

```csv
canonical_name,aliases,email,notion_user_id,active
吳宗芫,"吳宗芫|Joey|Joey_宗芫",joey@example.com,notion-user-id,true
```

## Notion 回填與例外處理

1. 成功：更新 Name、Date、派遣類型、Person，Status 設為 `Not started`。
2. 不確定或失敗：Status 設為 `內容待確認`，並在頁面內文寫入 AI 的 `issues` 與信心度。
3. 不會覆寫原始 PDF。

## 尚待完成的工項

- [ ] 移除舊的 `Read/Write Files from Disk` 節點（PDF 不需要落地）。
- [ ] 新增並連接「本機 PDF 擷取」節點。
- [ ] 在本機以 Docker Compose 啟動 `pdf-extractor`，測試一份新取得的 PDF。
- [ ] 建立 Gemini API credential。
- [ ] 建立並掛載人員對照 CSV。
- [ ] 建立 Gemini、姓名比對、Notion 更新與例外處理節點。
- [ ] 以一份測試派工單驗證後再 Publish。
