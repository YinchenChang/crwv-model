# CoreWeave 收支模型（v4.0）— Claude Code 工作守則

## 專案是什麼
CRWV 資金與評價模型，核心論點「Backlog 不是現金」。同一套引擎輸出兩個成品，數字必須完全一致：
- HTML（互動版，`build_html_portable.py` 產生）
- Excel（全部活公式，`build_xlsx.py` 產生）
此 repo 是日後 Nebius、Oracle、OpenAI 模型的模板。業務背景、目前結果與待辦見 `docs/` 內最新交接檔；技術細節見 `README.md`。

## 目錄
- `company.json`：公司原始輸入的**唯一來源**（HTML 與 Excel 共用）。換公司先改這裡。
- `segA.js`～`segE.js`、`tail.js`：HTML 引擎與畫面；`app_pretty.js`：模板函式庫片段來源。
- `build_xlsx.py`、`fix_outline.py`、`verify_ooxml.py`：Excel 建置與結構檢查。
- `cmp31.js`＋`xlx.py`（HTML vs Excel 數值）、`crawl.py`（畫面文字）、`xl_diff.py`（Excel 逐格）：核對工具。
- `dist/`：交付成品（HTML、xlsx）。`docs/`：交接檔、建置用模板 `template_v3_3.html`。

## 第一個任務（環境移植，完成前不要做其他改版）
原始碼原本在另一個沙盒執行，有寫死的路徑，需先移植：
0. 先檢查工具：`soffice --version`、`python3 -c "import openpyxl, playwright"`、Playwright 的 Chromium 能否啟動。雲端環境的 setup script 有 5 分鐘上限，可能沒裝完（紀錄在 `/tmp/crwv_setup.log`；v3 起只預裝 Python 套件）；缺什麼就在工作階段內補裝：`apt-get install -y --no-install-recommends libreoffice-calc-nogui`、`pip install --break-system-packages openpyxl pypdf playwright`、`python3 -m playwright install chromium`；Chromium 若因缺系統函式庫無法啟動，執行 `python3 -m playwright install-deps chromium`。回報時列出實際補裝了哪些。
1. 把 `/home/claude/...` 與 `/mnt/...` 的寫死路徑改為相對於 repo 根目錄（`build_xlsx.py` 的輸出、`fix_outline.py` 的 outline.json、`xlx.py` 的暫存檔、`build_html_portable.py` 的模板參數）。
2. 原本的 Excel 重算用沙盒內建的 `recalc.py`（此處沒有）：用 LibreOffice headless 自寫 `scripts/recalc.py`，功能＝開啟、全部重算、存檔，並回報公式錯誤數（#REF!、#DIV/0!、#VALUE!、#NAME?、#N/A）。
3. 新增 `scripts/verify.sh`，一次跑完：建 HTML → 建 Excel → 重算 → fix_outline → verify_ooxml → 三情境 xlx＋cmp31 → FY27 錨定 cmp31。任何一項失敗即非零結束。
4. 驗收：以 repo 內原始碼重建的 HTML／Excel，與 `dist/` 內 v4.0 成品比對：`crawl.py` 畫面文字 0 差異、`xl_diff.py --values` 0 差異、cmp31 三情境各 104 項全部 OK。

## 每次修改的鐵則
- 先讀交接檔與 README，再動手；純結構修改的驗收標準是「數字與畫面與前一版完全相同」。
- 每次修改後必跑 `scripts/verify.sh`，全數通過才可提交。改到數字的修改，要在回報中列出受影響的關鍵數字（三情境目標價等）前後對照。
- 版本號：**只有 `dist/` 成品（HTML 或 Excel）改變時才升版**；純工具修改（建置／核對腳本、文件、setup script 等，`dist/` 不變）不升版、不新增 VLOG。升版時 `vlog.py`（Excel 唯一來源）與 `tail.js` 的 VLOG（HTML）**兩處都要**新增一列；成品命名 `更新日_CoreWeave收支模型_v版本號`，放 `dist/`，並移除舊版成品。
- 同時更新交接檔（`docs/`）與 README。
- 一個任務一個分支、一個 PR；PR 說明寫：改了什麼、驗收結果、需 Andy 決定的事項。

## 勿改（踩過的坑）
1. 模板函式庫在 segA、segB 的插入點前是**未結束的 var 宣告鏈**：注入的第一句必須是 `COMPANY_DATA = {…};`，segB 第一行必須是 `PERIOD_LABELS = …,`，兩者都**不可加 var**。
2. 模板已宣告 `CO`，且其片段仍以 `Qk` 引用預設值：資料變數名為 `COMPANY_DATA`，並保留 `Qk = DEFAULTS` 別名。
3. 改名一律用 `rename_ids.py`（詞法分析，只改程式碼、不改畫面文字，含 `...name` 展開語法）；新名稱須先確認不存在於模板函式庫。
4. Excel `<sheetPr>` 子元素順序必須是 tabColor → outlinePr → pageSetUpPr，否則 Excel 回報「檔案損毀」；LibreOffice 與 openpyxl 不會發現，所以 `verify_ooxml.py` 必須通過。
5. 總結頁列印依賴 segD 的 `sumQ-np`、`sumQ-main` class。

## 待辦（依序；每項一個 PR）
1. 環境移植（上節）。
2. 目標價改為區間呈現（取代單點 45/55 加權）。
3. 一頁摘要＋市場共識對照；同時把同業 Comps（segB 的 lM、build_xlsx 的 peers）移入 company.json。共識數據由 Andy 在聊天中查證後提供資料檔，逐筆含來源、日期與標記（[Verified]／[Interested-party]…）；**不要自行杜撰或補數字**。
4. 季度層（Q3 財報 11/9 前完成）。
5. Excel 規範與精簡（色彩慣例、具名範圍、分頁合併、說明文字精簡）。
6. 其餘短名稱輔助函式改名（讀懂用途後才改）。

## 溝通
以繁體中文回報；專業、客觀、以事實為準。遇到需要判斷口徑（評價方法、預設值、評等門檻）的事項，停下來列出選項與影響，由 Andy 決定。
