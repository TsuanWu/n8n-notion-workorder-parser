# 搬遷與備份邊界

只搬 Notion 1006 與已確認為最新版本的股票解析；股票解析不屬本 Repository，若最新版在桌機，保留桌機版本。

| 目的位置 | 內容 |
| --- | --- |
| `D:\Docker\projects\n8n-notion-workorder-parser` | Git 程式、清理過的 workflow 範本及部署文件 |
| `D:\Docker\shared\n8n` | 真實 personnel-map.csv 與必要的共用檔案，不提交 Git |
| `D:\Docker\backups\<date>` | 未加密的原始 JSON、必要的環境設定、資料與備份清單，不提交 Git |

## 順序

1. 唯讀 inspect 兩台實際容器：Mounts、Image ID/digest、Port、Networks、環境變數來源及 Compose 標籤。報告只顯示敏感變數名稱。
2. 確認 n8n 使用 SQLite 或外部資料庫、binary data 儲存方式、credential 加密金鑰來源。先備份桌機現有 n8n，再處理筆電。
3. 若需完整回復備份，安排一致性備份窗口；運行中的 SQLite 不直接任意複製 database.sqlite 作為完整備份。資料庫、金鑰及必要 binary data 要成套保存。停止服務或建立備份容器需另行確認。
4. 將原始檔案備份與可分享的 Repository 分開。舊 tar.gz 不用於本次還原，也不把舊檔案重新壓縮後稱作最新 Volume 備份。
5. 保留桌機既有 Images 與 n8n_data。若需完整試還原，使用新 Volume、新容器名稱及不同測試 Port；勿覆蓋或合併既有 n8n_data。
6. 已有 n8n 時，只評估啟動 `compose.pdf-only.yaml`。先確認沒有同名/相同 DNS alias 的 PDF 服務，核對 CSV 檔案，並讓 n8n 與 PDF 服務加入正確網路。此 Compose 本身不會連接既有 n8n。
7. 選擇性匯入 Notion 範本並重新綁定 credentials/資源 ID；保持停用。股票流程先比對桌機與其他副本，不以舊 Draft 覆蓋。
8. 完成人員 CSV、PDF、Gemini、Notion 回填與附件檢查後，才安排正式切換。

## 尚未完成

目前只完成檔案層級備份與靜態範本檢查。Docker Engine 存取受限，未取得新的 Volume/資料庫/credentials 備份，也未驗證 live 工作流程。原始來源 CSV 是否等同容器目前掛載版本仍待 inspect。

`.gitignore` 不能保護已追蹤檔案，也不能移除 Git 歷史中的資料；每次提交前仍須檢查完整差異。備份壓縮檔與原始 JSON 不上傳 GitHub。
