# CoreWeave 收支模型 v4.0 原始碼包

HTML 與 Excel 都由這裡的原始碼產生。新對話中若要修改模型，請把本資料夾解壓到 `/home/claude/`，並同時上傳 v4.0 的 HTML（作為函式庫模板）。

## 檔案
| 檔案 | 用途 |
|---|---|
| segA.js | 資金引擎：情境、產能與收入、CapEx／折舊、租金、期前融資瀑布、連動檢查、敏感性、反向 DCF（rvQ） |
| segB.js | 評價引擎：損益、DCF（0 截斷／選擇權、失效條件）、EV/EBITDA、加權目標價、同業資料 |
| segC.js | 「損益與評價」頁 UI（損益簡表、Comps、DCF、目標價、反向 DCF） |
| segE.js | 「總結」簡報頁 UI（v3.4 新增）：8 張 1280×720 投影片、簡報模式、列印 CSS；數字即時取自 dA／TM／rvQ／pA |
| segD.js | 頁首與頁籤（總結｜資金模型｜損益與評價）、「資金模型」頁 UI（標題摘要、左欄分類選單、各模組分頁、新債與新股、版本紀錄） |
| tail.js | 共用元件：Excel 式表格 BM、浮動說明 tipQ、分類選單 accQ、兩層選單 navQ、FMODS／VMODS、VLOG |
| app_pretty.js | 原 Oracle 模板的美化程式碼（取其中三段共用 UI） |
| rm_andy.js | Andy 修改過的開關元件（說明改為浮動提示） |
| build_html_portable.py | 組裝 HTML：`python3 build_html_portable.py 3.6 輸出.html <更新日> 20260924_CoreWeave收支模型_v4_0.html`（組裝順序：segA、模板段、segB、模板段、segC、模板段、segD、tail、segE） |
| build_xlsx.py | 產生 Excel（輸出路徑與版本號寫在檔尾 wb.save 與導覽 A1；自同目錄讀取 vlog.py、rv_snap.json；輸出到 /home/claude/out/，執行前先 `mkdir -p /home/claude/out`） |
| fix_outline.py | LibreOffice 重算後，補回 Excel 群組按鈕位置與收合狀態：`python3 fix_outline.py 檔案.xlsx`（v3.4 修正：outlinePr 依 schema 放在 tabColor 之後） |
| verify_ooxml.py | Excel 嚴格結構檢查（XML 格式、工作表與 sheetPr 子元素順序）；v3.4 新增 |
| vlog.py | 版本紀錄資料，Excel 的唯一來源（v3.4 起 build_xlsx.py 直接 import，不再內嵌副本）；HTML 的 VLOG 在 tail.js 末尾，需同步 |
| rv_snap.json | 反向 DCF 快照（Excel「評價_反向DCF」頁使用；以 node 執行 segA+segB 的 rvQ 重算） |
| xlx.py／cmp31.js | 一致性核對：xlx.py 依情境重算 Excel 並擷取數值；cmp31.js 以 HTML 引擎逐列比對（三情境各 93 項） |

## Excel 產生流程
1. `mkdir -p /home/claude/out && python3 build_xlsx.py`
2. `python3 /mnt/skills/public/xlsx/scripts/recalc.py <xlsx> 120`
3. `python3 fix_outline.py <xlsx>`
4. Excel 結構核對：`python3 verify_ooxml.py <xlsx>` 必須輸出 `OOXML OK`（LibreOffice／openpyxl 能開不代表 Excel 能開）
5. 數值核對：`for s in 1 2 3; do python3 xlx.py <xlsx> $s xl17_$s.json; done`，再 `node cmp31.js low|base|high`（輸出 OK 行數）

## 注意
- 新增到 tail.js 或 seg 檔的全域名稱，必須避開模板函式庫已用的名稱（例如 nf、XS、Hd、Tp 都會衝突），慣例是加 Q 字尾。
- LibreOffice 不支援 NORM.S.DIST，Excel 公式請用 NORMSDIST。

- 列印：總結頁的列印 CSS 依賴 segD 的 `sumQ-np`（頁首、頁籤）與 `sumQ-main`（主容器）兩個 class，修改 segD 時請保留。
- 目視檢查可用 Playwright：開啟 HTML、`page.pdf(prefer_css_page_size=True)` 應得 8 頁。

## v3.5 核對方式（EV/EBITDA 錨定年度）
- 預設三情境：`python3 xlx.py <xlsx> 1|2|3 xl17_<n>.json`，再 `node cmp31.js low|base|high`（目前各 104 項）。
- 其他錨定年度：`python3 xlx.py <xlsx> 2 xl17_2_a3.json 3` 後 `node cmp31.js base 3`（第 4 個參數＝錨定年度 1–4）。
- 矩陣：HTML `evGrid()`（segB）與 Excel「評價_DCF與目標價」的「錨定×倍數｜…」列逐格比對（40 格）。

## v4.0 架構：公司資料單一來源
- **company.json**：所有公司原始輸入（HTML 引擎與 Excel 共用）。換公司時先改這個檔；衍生值（情境 Billable 比率、Q3 新增 RPO 權重、債務合計與平均利率）留在 segA 開頭由程式推導。
- HTML：`build_html_portable.py` 把 company.json 注入為 `COMPANY_DATA`，segA 開頭讀取。Excel：`build_xlsx.py` 開頭讀同一檔（75 項輸入，百分點欄位以 `PCT_()` 轉成比例）。
- 頂層鍵：

| 鍵 | 型別 |
|---|---|
| `meta` | dict |
| `periods` | list |
| `periodYears` | list |
| `actual1H` | dict |
| `historicalPL` | list |
| `rpo` | dict |
| `leases` | dict |
| `debt` | dict |
| `latestQuarter` | dict |
| `callFacts` | dict |
| `scenarios` | dict |
| `legacy` | dict |
| `defaults` | dict |
| `valuation` | dict |
| `methodology` | dict |

### 建置時的兩個陷阱（勿改）
1. 模板函式庫在 segA、segB 的插入點前都是**未結束的 var 宣告鏈**，所以注入的第一句必須是 `COMPANY_DATA = {…};`，segB 第一行必須是 `PERIOD_LABELS = …,`（兩者都不可加 `var`）。
2. 模板函式庫本身已宣告 `CO`，且其片段仍以 `Qk` 引用預設值：因此資料變數名為 `COMPANY_DATA`，並保留 `Qk = DEFAULTS` 別名。

### 識別字改名對照（rename_ids.py；只改程式碼，不改畫面文字）
| 舊名 | 新名 |
|---|---|
| `zk` | `PERIODS` |
| `Lq` | `PERIOD_YEARS` |
| `Bk` | `UPDATE_DATE` |
| `Vk` | `SOURCE_ORDER_NOTE` |
| `H1` | `ACTUAL_1H` |
| `Uk` | `RPO_SCHEDULED_SHARE` |
| `Wk` | `RPO_BUCKET_W` |
| `Gk` | `RPO_Q3ADD_W` |
| `Kk` | `LEASE_CASH_ON_BAL` |
| `qk` | `DEBT_AMORT` |
| `Jk` | `LEASE_AFTER_FY30` |
| `Yk` | `LATEST_Q` |
| `Xk` | `CALL_FACTS` |
| `Zk` | `SCENARIOS` |
| `Qk` | `DEFAULTS` |
| `DBT` | `DEBT_TOOLS` |
| `LSE` | `LEASE_FACTS` |
| `cM` | `VAL_DEFAULTS` |
| `oM` | `PERIOD_LABELS` |
| `sM` | `HIST_PL` |
| `dA` | `runFunding` |
| `TM` | `runValuation` |
| `rvQ` | `reverseDcf` |
| `pA` | `sensitivities` |
| `oA` | `rpoBridge` |
| `evGrid` | `evAnchorGrid` |
| `gM` | `dcfValue` |
| `vM` | `evEbitdaLeg` |
| `xM` | `blendCall` |
| `hM` | `forwardPL` |
| `pM` | `shareCount` |
| `SM` | `dcfGridWaccG` |
| `yM` | `BLEND_W` |

尚未改名（用途未逐一確認，留待後續）：segA 的 eA、tA、nA、rA、iA、aA、sA、cA、lA、uA、fA；segB 的 uM、dM、mM、mR、wM、EM；segC 的 AM；segD 的 zM；tail 的 BM、VM；格式化函式 Y、mA、hA（模板片段也使用，不可改）。

### 尚未移入 company.json
同業 Comps 數據（segB 的 lM 與 build_xlsx 的 peers）、「來源」頁與站點說明等長文字。換公司時仍需手動改這些地方。

### v4.0 核對工具
- `load_engine.js`：在 node 載入 company.json＋segA＋segB（cmp31.js 使用）。
- `xl_diff.py a.xlsx b.xlsx [--values]`：Excel 逐格比對（公式或重算後的值）。
- `crawl.py <html> <out.json>`：逐頁逐分頁擷取畫面文字，用於比對兩版 HTML 的顯示是否相同。
- 結構性修改的驗收標準：cmp31 三情境全數一致；crawl 比對除版本紀錄外 0 差異；xl_diff 除版本紀錄外 0 差異。
