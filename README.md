# CoreWeave 收支模型 v4.3 原始碼包

HTML 與 Excel 都由這裡的原始碼產生。所有路徑皆相對於 repo 根目錄；建置產物寫到 `out/`（不納入版控），交付成品放 `dist/`。HTML 的函式庫模板為 `docs/template_v3_3.html`。

各任務的完整回報（改了什麼、verify.sh 輸出、關鍵數字對照、待決事項）存於 `docs/reports/`。

**一鍵建置與核對**：`scripts/verify.sh`（純結構修改加 `--vs-dist`，另與 `dist/` 成品比對畫面文字與 Excel 數值、公式；v4.2 起 Excel 以列名稱配對，見「v4.2 核對方式」）。

**換公司**：先讀下方「company.json 欄位說明（換公司填表指引）」。任何一項失敗即以非零代碼結束。

## 檔案
| 檔案 | 用途 |
|---|---|
| segA.js | 資金引擎：情境、產能與收入、CapEx／折舊、租金、期前融資瀑布、連動檢查、敏感性、反向 DCF（rvQ） |
| segB.js | 評價引擎：損益、DCF（0 截斷／選擇權、失效條件）、EV/EBITDA、加權目標價、目標價區間（`targetRange`，v4.1）、評等規則 `rateCall`（門檻讀 `methodology.rating`，v4.2）；同業資料 `lM` 由 `company.json` → `peers` 產生（v4.2）；市場共識對照 `consensusView`、共識逐筆清單 `consensusItems`、來源頁引用句 `consSourceTxtQ`（v4.3） |
| segC.js | 「損益與評價」頁 UI（損益簡表、Comps、DCF、目標價、反向 DCF；v4.3「市場共識」分頁＝segE 的 `ConsTabQ`） |
| segE.js | 「總結」簡報頁 UI（v3.4 新增）：10 張 1280×720 投影片（v4.3 第 1 張為一頁摘要 `onePageQ`，其餘 9 張為附錄）、簡報模式、列印 CSS；「市場共識」分頁 `ConsTabQ`（v4.3）；數字即時取自 runFunding／runValuation／reverseDcf／sensitivities |
| segD.js | 頁首與頁籤（總結｜資金模型｜損益與評價）、「資金模型」頁 UI（標題摘要、左欄分類選單、各模組分頁、新債與新股、版本紀錄） |
| tail.js | 共用元件：Excel 式表格 BM、浮動說明 tipQ、分類選單 accQ、兩層選單 navQ、FMODS／VMODS、VLOG |
| app_pretty.js | 原 Oracle 模板的美化程式碼（取其中三段共用 UI） |
| rm_andy.js | Andy 修改過的開關元件（說明改為浮動提示） |
| build_html_portable.py | 組裝 HTML：`python3 build_html_portable.py 4.0 out/輸出.html 2026-09-24 [模板 HTML]`（模板省略時用 `docs/template_v3_3.html`；組裝順序：segA、模板段、segB、模板段、segC、模板段、segD、tail、segE） |
| build_xlsx.py | 產生 Excel：`python3 build_xlsx.py [輸出.xlsx]`（預設 `out/20260925_CoreWeave收支模型_v4_3.xlsx`；版本號、更新日、市價日寫在導覽 A1（v4.3 起讀 vlog.py 與 company.json）；自同目錄讀取 vlog.py、rv_snap.json、company.json 與 `meta.consensusFile` 指定的共識資料檔；群組資訊寫到 `out/outline.json`） |
| fix_outline.py | LibreOffice 重算後，補回 Excel 群組按鈕位置與收合狀態：`python3 fix_outline.py 檔案.xlsx [outline.json]`（預設讀 `out/outline.json`；v3.4 修正：outlinePr 依 schema 放在 tabColor 之後） |
| fix_datatable.py | v4.1：LibreOffice 重算後，把模擬運算表（情境區間）由 `TABLE()` 一般公式還原為 Excel 的 `dataTable` 公式，保留算出的值：`python3 fix_datatable.py 檔案.xlsx` |
| verify_ooxml.py | Excel 嚴格結構檢查（XML 格式、工作表與 sheetPr 子元素順序；v4.1 起另檢查模擬運算表存在且無殘留 `TABLE()`）；v3.4 新增 |
| vlog.py | 版本紀錄資料，Excel 的唯一來源（v3.4 起 build_xlsx.py 直接 import，不再內嵌副本）；HTML 的 VLOG 在 tail.js 末尾，需同步 |
| rv_snap.json | 反向 DCF 快照（Excel「評價_反向DCF」與「摘要」頁使用）；現價或預設輸入改變後以 `node scripts/rv_snap.js` 重新產生（v4.3） |
| data/consensus_crwv_20260925.json | 市場共識資料檔（v4.3；Andy 查證後提供，只讀，不得增補或修改數字）；路徑寫在 `company.json` → `meta.consensusFile`，HTML 建置時併入 `COMPANY_DATA.consensus`，Excel 直接讀取 |
| xl_diff.py | Excel 比對：`python3 xl_diff.py 舊.xlsx 新.xlsx [--values] [--by-label] [--ignore=工作表,…]`（v4.2 `--by-label`：新增列造成位移時以「區段＋列名稱」配對，見「v4.2 核對方式」；v4.3 `--ignore`：兩檔都略過指定工作表） |
| scripts/fields_doc.py | v4.2：產生下方「company.json 欄位說明」的表格（`python3 scripts/fields_doc.py > out/fields.md`）；company.json 有欄位沒寫說明即報錯 |
| xlx.py／cmp31.js | 一致性核對：xlx.py 依情境重算 Excel 並擷取數值（暫存檔在 `out/`，以 `scripts/recalc.py` 重算）；cmp31.js 以 HTML 引擎逐列比對（三情境各 200 項，含 v4.1 目標價區間與判斷句、v4.3 市場共識逐筆與一頁摘要的差距、隱含倍數與四個句子逐字比對；讀取目前目錄的 `xl17_*.json`） |
| scripts/recalc.py | LibreOffice headless 重算：`python3 scripts/recalc.py 檔案.xlsx [逾時秒數]`＝開啟、全部重算、原地存檔，輸出 JSON 並回報公式錯誤數（#REF!、#DIV/0!、#VALUE!、#NAME?、#N/A）；有錯誤或失敗時代碼 1 |
| scripts/verify.sh | 一次跑完建置與核對（見下節） |
| scripts/cloud_setup.sh | 雲端環境 setup script（只裝 Python 套件；LibreOffice Calc 於工作階段內補裝，見 CLAUDE.md） |

## Excel 產生流程（scripts/verify.sh 步驟 2–7 即為此流程）
1. `python3 build_xlsx.py`（輸出到 `out/`）
2. `python3 scripts/recalc.py out/<xlsx> 120`（必須回報 `"total_errors": 0`）
3. `python3 fix_outline.py out/<xlsx>`，再 `python3 fix_datatable.py out/<xlsx>`（v4.1：還原模擬運算表；未執行時 verify_ooxml 會失敗）
4. Excel 結構核對：`python3 verify_ooxml.py out/<xlsx>` 必須輸出 `OOXML OK`（LibreOffice／openpyxl 能開不代表 Excel 能開）
5. 數值核對：`for s in 1 2 3; do python3 xlx.py out/<xlsx> $s out/xl17_$s.json; done`，再於 `out/` 內 `node ../cmp31.js low|base|high`（輸出 OK 行數）

## 執行環境需求
- Python 3.11 以上＋`openpyxl`、`playwright==1.56.0`（`crawl.py`；對應雲端環境預裝的 Chromium build 1194，見 `scripts/cloud_setup.sh`）、`pypdf`；Node 18 以上（`structuredClone`）。
- LibreOffice **含 Calc 模組**（Debian／Ubuntu：`libreoffice-calc-nogui`）。只有 `libreoffice-core` 時 `soffice --version` 正常，但開啟 xlsx 會停住；`scripts/recalc.py` 逾時會提示此原因。
- 未設 locale 的環境（`LANG` 為空）下 LibreOffice 會把中文檔名轉成 `??`：`scripts/recalc.py` 已固定 `LC_ALL=C.UTF-8` 並以 file URL 傳遞路徑。
- `crawl.py`：Playwright 預設的 Chromium 無法啟動時（例如 playwright 未固定版本、與預裝 Chromium 不符），改用環境變數 `CHROMIUM_PATH`，未設時用 `/opt/pw-browsers/chromium`。

## 注意
- 新增到 tail.js 或 seg 檔的全域名稱，必須避開模板函式庫已用的名稱（例如 nf、XS、Hd、Tp 都會衝突），慣例是加 Q 字尾。
- LibreOffice 不支援 NORM.S.DIST，Excel 公式請用 NORMSDIST。

- 列印：總結頁的列印 CSS 依賴 segD 的 `sumQ-np`（頁首、頁籤）與 `sumQ-main`（主容器）兩個 class，修改 segD 時請保留。
- 目視檢查可用 Playwright：開啟 HTML、`page.pdf(prefer_css_page_size=True)` 應得 10 頁（v4.3：一頁摘要＋附錄 9 頁）。

## v3.5 核對方式（EV/EBITDA 錨定年度）
- 預設三情境：`python3 xlx.py <xlsx> 1|2|3 xl17_<n>.json`，再 `node cmp31.js low|base|high`（目前各 200 項）。
- 其他錨定年度：`python3 xlx.py <xlsx> 2 out/xl17_2_a3.json 3` 後於 `out/` 內 `node ../cmp31.js base 3`（第 4 個參數＝錨定年度 1–4）。
- 矩陣：HTML `evGrid()`（segB）與 Excel「評價_DCF與目標價」的「錨定×倍數｜…」列逐格比對（40 格）。

## v4.1 目標價區間
- **點位**：目前輸入的加權目標價（評等仍依點位，規則不變；規則抽成 segB 的 `rateCall`，`blendCall` 共用）。
- **情境區間（A）**：保守與積極情境的加權目標價，取 min／max（保守情境擴張最少、目標價最高）。HTML 以 `scnQ`（v4.1 自 segE 移到 segB）換情境、保留其餘手動調整；Excel 以「輸入與假設」底部 H 區的模擬運算表計算（輸入格＝情境選擇；Excel 規定輸入格與運算表須在同一工作表）。
- **方法區間（B）**：目前輸入，EV/EBITDA 倍數換成 `company.json` → `methodology.rangeMultiples`（預設 5、6）；Excel 輸入在 F 區「方法區間倍數：下端／上端」。
- **判斷句**：情境區間上緣與現價比較，並依三情境實際評等說明賣出是否在三個情境下都成立；任一情境與賣出門檻（現價 × 85%）的距離小於現價 5% 時揭露該距離。
- **DCF 權重說明**：只在 DCF 被 0 截斷時顯示；DCF 失效時改為一句；DCF 為正或選擇權模式時不顯示。
- 字串在 `targetRange()` 產生，HTML 各頁共用；Excel 以文字公式（`TEXT(x,"0.0")` 等）產生同一字串，cmp31 逐字比對。
- 模擬運算表的建置鏈：build_xlsx 以 openpyxl 寫入 `t="dataTable"` → LibreOffice 能正確計算，但存檔時改寫成 `TABLE(公式列,輸入格,輸入值)` → `fix_datatable.py` 還原為單一 `dataTable` 公式（只放在區塊左上格）。本環境沒有 Microsoft Excel，結構依 ECMA-376；Excel 實機開檔由 Andy 於合併前確認（v4.2：2026-09-25 確認正常）。

## v4.2 設定集中（同業 Comps、評等門檻）
- **同業 Comps**：數字、名稱、備註與 Comps 分頁的說明文字都在 `company.json` → `peers`；segB 的 `lM` 由 `peers.list` 產生（EV＝市值＋淨負債、EBITDA＝營業損益＋D&A 現算），build_xlsx「可比公司」頁讀同一份。名稱與備註暫時保留 HTML、Excel 兩種寫法（`labelHtml／labelXlsx`、`noteHtml／noteXlsx`），統一另開任務。Excel CRWV 列改讀 `callFacts`／`latestQuarter`。
- **評等門檻**：`company.json` → `methodology.rating`（7 項，見欄位說明）。HTML：`rateCall`、`blendCall`、`targetRange` 與含門檻的畫面文字（`pctQ`／`multTxt` 組字）。Excel：「輸入與假設」F 區尾端「▸ 評等門檻」7 格；評等代碼、賣出門檻價、判斷句的餘裕揭露、「檢查」頁的終值與股權條件都引用這些格；評等規則說明句與檢查頁的標準欄改為文字公式，改門檻時跟著變。cmp31 以標籤為鍵的「賣出門檻價（現價 × (1 − 15%)）」列，標籤由門檻值產生。
- **不移入的技術容忍值**：現價下限 0.01（避免除以 0）、股權需求 ≤0.01bn 視為不需新股。

### v4.2 核對方式（新增輸入列造成的位移）
- `scripts/verify.sh --vs-dist` 的 Excel 比對改用 `xl_diff.py --by-label`：兩檔列數或 A 欄不同的工作表，以「區段＋A 欄列名稱」配對（區段＝上方最近的第一層區段標題列，淺藍底），其餘工作表仍逐格比對。
- 配對鍵重複、或 A 欄空白的列有內容時直接報錯並列出，不自行配對。新版多出的列另列「新增列」清單，不計為差異。
- 公式比對時，舊版公式的列號（含跨工作表引用）依列對照換算後再比。另有兩類變更列清單、不計為差異：「常數改為引用輸入格」（把引用換回該格常數後與舊版公式相同）、「文字改為活公式」（重算後的值與舊版文字相同）。
- 以不同門檻測試過連動：把 `methodology.rating` 改成其他值後重建，cmp31 三情境＋FY27 錨定仍全部一致（HTML 與 Excel 同步改變）。

## v4.3 一頁摘要與市場共識
- **共識資料**：只讀 `data/consensus_crwv_20260925.json`（路徑在 `company.json` → `meta.consensusFile`）；不增補、不修改數字，資料檔沒有的欄位顯示「未列」。建置時檢查兩件事，不符即停止：共識檔的 Q3 營收指引與 `callFacts.q3RevLo／q3RevHi` 相同（以 company.json 為準）；`actual1H.adjEbitda`＝Q1＋Q2。
- **逐筆顯示**：`consensusItems()`（segB）與 build_xlsx 的 `cons_items()` 產生同一組列（標籤以「共識｜」開頭）：HTML「損益與評價 → 市場共識」分頁、Excel「輸入與假設」I 區（C–E 數值、F 擷取日期、G 標記、I 來源、J 備註）。另揭露 `sourceIndependence`（兩網站的數字都來自 S&P，不是獨立交叉驗證）與「未取得」清單。
- **與市場的差異**（`consensusView()`）：模型用目前情境（預設＝基準）；FY26 為全年口徑：營收＝1H 實際＋2H 模型、調整後 EBITDA＝1H 實際調整後 EBITDA 2.667（Q1 1.157＋Q2 1.510，報導轉述 [Verified]，只用於此比較）＋2H 模型、CapEx＝1H 實際毛額 16.139＋2H 模型毛額。差距＝模型 ÷ 共識 − 1；EBITDA 率以百分點列；淨負債只列不判斷（共識口徑未揭露）。
- **判斷句**：營收、EBITDA、CapEx 任一項差距絕對值超過 `methodology.consensusGapTol`（5%）即為分歧；句子寫出分歧起始年與之後各年超過門檻的項目。
- **隱含倍數**：（價格 × 模型股數 0.587bn＋共識 FY28 淨負債）÷ 共識 FY28 調整後 EBITDA，價格分別用共識平均目標價與現價；與方法區間上緣（6x）並列。
- **一頁摘要**：HTML 總結頁第 1 頁（`onePageQ`；原 9 頁順延為附錄，列印 10 頁）；Excel「摘要」分頁（「導覽」之後，全部活公式）。四個句子（結論句、共識判斷句、隱含倍數句、Q3 句）由 HTML 函式與 Excel 文字公式各自產生，cmp31 逐字比對。反向 DCF 在 Excel 引用快照（`rv_snap.json`）。
- **現價**：$90.13（2026-09-24 收盤）；股權發行參考價同步。Comps 表的 CRWV 市值維持 9/21（與同業同一天）；股權／可轉債金額維持 6.2bn（Andy 決定）。
- **核對**：B＋C（現價不變）先與 v4.2 比對：Excel 用 `xl_diff.py --by-label --ignore=來源,摘要`（值與公式 0 差異，新增列 64）；畫面文字差異限於新頁、Street 列刪除、來源句、附錄前綴與頁碼。再做 A（改現價）並列出數字對照（見 `docs/reports/20260925_一頁摘要與市場共識.md`）。

## company.json 欄位說明（換公司填表指引）
換成 Nebius、Oracle、OpenAI 等公司時，照這一節逐欄填寫 `company.json`；HTML 與 Excel 都從這個檔讀資料，改完執行 `scripts/verify.sh`。

**填表慣例**
- 金額單位是**十億美元（US$bn）**，例如 4.653 代表 46.53 億美元；另有標示的例外：每股（US$）、每 MW 建置成本（百萬美元／MW，US$m/MW）、股數（十億股，bn）。
- 「比例」寫成小數（0.25＝25%）；標示「%」的欄位寫成百分點（25＝25%）。兩種寫法沿用既有程式，不可混用。
- 「清單」依模型期順序填：FY26 下半年、FY27、FY28、FY29、FY30，共 5 格（除非另有說明）。
- 文字中的來源標記沿用 [Verified]（已公開可查）、[Interested-party]（利害關係人說法）、[Derived]（由其他數字換算）、[Assumed]（判斷值）。
- 「換公司」欄：**必改**＝公司特有的資料；**檢查**＝判斷值，要依新公司重新評估；**可沿用**＝口徑或方法，通常不必改。
- 下表的「目前數值」是 CoreWeave v4.3 的值；過長的文字只顯示開頭。表格由 `scripts/fields_doc.py` 產生，新增欄位時先在該檔補說明，再重新產生。
### `meta`：基本資料

| 欄位 | 意義 | 單位 | 目前數值 | 換公司 |
|---|---|---|---|---|
| `meta.company` | 公司名稱 | 文字 | CoreWeave | 必改 |
| `meta.ticker` | 股票代號 | 文字 | CRWV | 必改 |
| `meta.updateDate` | 資料更新日 | 日期 | 2026-09-25 | 必改 |
| `meta.priceDate` | 股價日期（現價的收盤日；畫面與 Excel 的現價日期都讀這格） | 日期 | 2026-09-24 | 必改 |
| `meta.consensusFile` | 市場共識資料檔路徑（v4.3；只讀，由使用者查證後提供；建置時併入 HTML、Excel 讀同一檔） | 路徑 | data/consensus_crwv_202609… | 必改 |
| `meta.sourceOrderNote` | 資料來源的先後與衝突時的取捨原則（畫面說明文字） | 文字 | 時序先法說（8/11）、後 10-Q（8/12）、再… | 必改 |

### `periods`：模型期

| 欄位 | 意義 | 單位 | 目前數值 | 換公司 |
|---|---|---|---|---|
| `periods` | 模型期的名稱，共 5 期 | 文字清單 | FY26、FY27、FY28、FY29、FY30 | 檢查 |
| `periodYears` | 每一期的長度；第一期是半年，所以是 0.5 | 年 | 0.5、1、1、1、1 | 檢查 |

### `actual1H`：上半年實際數（10-Q）

| 欄位 | 意義 | 單位 | 目前數值 | 換公司 |
|---|---|---|---|---|
| `actual1H.label` | 「上半年實際數」的標題 | 文字 | 1H26 實際（10-Q） | 必改 |
| `actual1H.cash1231` | 上一年底現金 | US$bn | 3.127 | 必改 |
| `actual1H.revenue` | 上半年營收 | US$bn | 4.653 | 必改 |
| `actual1H.capex` | 上半年資本支出（認列口徑，含設備商融資） | US$bn | 16.139 | 必改 |
| `actual1H.cashCapex` | 上半年現金購置固定資產 | US$bn | 14.117 | 必改 |
| `actual1H.interest` | 上半年利息費用 | US$bn | 1.176 | 必改 |
| `actual1H.leasePaid` | 上半年租賃現金支付 | US$bn | 0.748 | 必改 |
| `actual1H.debtRepaid` | 上半年還款 | US$bn | 5.219 | 必改 |
| `actual1H.borrow` | 上半年借款 | US$bn | 16.747 | 必改 |
| `actual1H.equity` | 上半年股權募資 | US$bn | 2.982 | 必改 |
| `actual1H.cappedCall` | 上半年 capped call（可轉債配套避險）支出 | US$bn | 0.492 | 必改 |
| `actual1H.jv` | 上半年合資（JV）與策略投資出資 | US$bn | 0.688 | 必改 |
| `actual1H.cfo` | 上半年營運現金流 | US$bn | 3.663 | 必改 |
| `actual1H.prepay` | 上半年客戶預付（遞延收入淨流入） | US$bn | 1.365 | 必改 |
| `actual1H.da` | 上半年折舊攤銷 | US$bn | 2.54 | 必改 |
| `actual1H.sbc` | 上半年股份基礎薪酬 | US$bn | 0.318 | 必改 |
| `actual1H.opInc` | 上半年 GAAP 營業損益 | US$bn | -0.193 | 必改 |
| `actual1H.ni` | 上半年淨損益 | US$bn | -1.366 | 必改 |
| `actual1H.eps` | 上半年 GAAP 每股盈餘 | US$ | -2.53 | 必改 |
| `actual1H.ngEps` | 上半年每股盈餘（加回股份基礎薪酬） | US$ | -1.94 | 必改 |
| `actual1H.adjEbitda` | 上半年調整後 EBITDA（v4.3；只用於與市場共識比較 FY26，不進模型損益與評價） | US$bn | 2.667 | 必改 |
| `actual1H.adjEbitdaMeta` | 上述數字的 Q1／Q2 拆分、來源、標記與備註（建置時檢查 Q1＋Q2＝合計） | 物件 | 物件（q1、q2、tag、sources、crossCheck、note、usage） | 必改 |

### `historicalPL`：歷年損益

| 欄位 | 意義 | 單位 | 目前數值 | 換公司 |
|---|---|---|---|---|
| `historicalPL` | 歷年損益，一年一列（損益頁的歷史欄）。每列欄位：year 年度、revenue 營收、opInc GAAP 營業損益、ni 淨損益（以上 US$bn）、eps GAAP 每股盈餘、ngEps 加回股份基礎薪酬的每股盈餘（US$）、shares 加權流通股數（bn）、tag 來源標記 | 清單 | 4 筆 | 必改 |

### `rpo`：已簽約未認列營收（RPO）

| 欄位 | 意義 | 單位 | 目前數值 | 換公司 |
|---|---|---|---|---|
| `rpo.scheduledShare` | 剩餘履約義務（RPO，已簽約未認列的營收）預計在模型期內認列的比例 | 比例 | 0.84 | 必改 |
| `rpo.bucketWeights` | RPO 在五期（FY26 下半年、FY27、FY28、FY29、FY30）各期認列的比例，合計等於上一欄 | 比例清單 | 0.1025、0.205、0.2、0.195、0.1375 | 必改 |

### `leases`：租約

| 欄位 | 意義 | 單位 | 目前數值 | 換公司 |
|---|---|---|---|---|
| `leases.onBalanceCash` | 已入帳租約在五期（FY26 下半年、FY27、FY28、FY29、FY30）各期的現金租金 | US$bn 清單 | 1.04、2.339、2.306、2.373、2.289 | 必改 |
| `leases.afterFY30` | 已入帳租約在模型期之後還要付的租金合計 | US$bn | 19.023 | 必改 |
| `leases.facts.onBal` | 已入帳租約未折現付款合計 | US$bn | 29.37 | 必改 |
| `leases.facts.notCommenced` | 已簽約但尚未起租的租約（表外） | US$bn | 35.5 | 必改 |
| `leases.facts.singleCap` | 單一大型站點的租金上限（10-Q 揭露） | US$bn | 14.7 | 必改 |
| `leases.facts.share` | 第三方租賃占機房取得的比例（用於租金基準檢驗） | 比例 | 0.85 | 檢查 |
| `leases.operatingPayments` | 營業租賃到期表：五期各期，最後一格為之後合計（Excel 租賃頁） | US$bn 清單 | 1.028、2.116、2.306、2.373、2.289、19.023 | 必改 |
| `leases.financePayments` | 融資租賃到期表：同上格式 | US$bn 清單 | 0.012、0.223、0、0、0、0 | 必改 |

### `debt`：既有債務

| 欄位 | 意義 | 單位 | 目前數值 | 換公司 |
|---|---|---|---|---|
| `debt.amortization` | 既有債務在五期（FY26 下半年、FY27、FY28、FY29、FY30）各期的排程還本 | US$bn 清單 | 4.413、6.184、4.416、2.421、3.221 | 必改 |
| `debt.amortAfterFY30` | 模型期之後的還本合計 | US$bn | 14.896 | 必改 |
| `debt.instruments` | 既有債務逐筆明細，一筆一列：[名稱, 追索／非追索, 到期, 有效利率（比例）, 本金（US$bn）, 備註]。加總本金須等於 10-Q 本金合計 | 清單 | 16 筆 | 必改 |
| `debt.convertible.principal` | 期後新發行可轉債本金（不在五期還本表內，只計利息） | US$bn | 3.7 | 必改 |
| `debt.convertible.coupon` | 該可轉債票面利率 | 比例 | 0.02875 | 必改 |

### `latestQuarter`：最新一季財報數字（10-Q）

換公司：全部必改（公司特有資料）。「程式使用」為否的欄位只是存檔備查，畫面與 Excel 的說明文字目前另外寫在程式裡。

| 欄位 | 意義 | 單位 | 目前數值 | 程式使用 |
|---|---|---|---|---|
| `filed` | 申報日 | 日期 | 2026-08-12 | 否 |
| `periodEnd` | 季末日 | 日期 | 2026-06-30 | 否 |
| `revenue` | 當季營收 | US$bn | 2.575 | 是 |
| `yoy` | 當季營收年增率 | 比例 | 1.12 | 是 |
| `h1Revenue` | 上半年營收 | US$bn | 4.653 | 是 |
| `costRev` | 當季營收成本 | US$bn | 0.879 | 否 |
| `techInfra` | 當季技術與基礎設施費用 | US$bn | 1.507 | 否 |
| `opInc` | 當季 GAAP 營業損益 | US$bn | -0.049 | 否 |
| `interest` | 當季利息費用 | US$bn | 0.64 | 否 |
| `h1Interest` | 上半年利息費用 | US$bn | 1.176 | 否 |
| `ni` | 當季淨損益 | US$bn | -0.626 | 否 |
| `h1Ni` | 上半年淨損益 | US$bn | -1.366 | 否 |
| `epsDiluted` | 當季稀釋每股盈餘 | US$ | -1.14 | 否 |
| `sbc` | 當季股份基礎薪酬 | US$bn | 0.165 | 否 |
| `da` | 當季折舊攤銷 | US$bn | 1.393 | 否 |
| `adjEbitda` | 當季調整後 EBITDA | US$bn | 1.51 | 否 |
| `adjOpInc` | 當季調整後營業利益 | US$bn | 0.128 | 否 |
| `rpo` | 季末 RPO | US$bn | 103.7 | 是 |
| `backlog` | 季末 backlog（含其他） | US$bn | 104.2 | 否 |
| `rpo24m` | RPO 於 24 個月內認列比例 | 比例 | 0.41 | 否 |
| `rpo25to48` | RPO 於 25–48 個月認列比例 | 比例 | 0.39 | 否 |
| `rpo49to78` | RPO 於 49–78 個月認列比例 | 比例 | 0.2 | 否 |
| `cash` | 季末現金 | US$bn | 5.524 | 否 |
| `restricted` | 受限現金 | US$bn | 1.38 | 否 |
| `marketable` | 有價證券 | US$bn | 0.015 | 否 |
| `availability` | 未動用信用額度 | US$bn | 10.014 | 是 |
| `debtPrincipal` | 債務本金合計 | US$bn | 35.551 | 是 |
| `recourseNet` | 追索債務淨額 | US$bn | 31.405 | 否 |
| `nonRecourseNet` | 非追索債務淨額 | US$bn | 3.663 | 否 |
| `ddtlOut` | DDTL 未償餘額 | US$bn | 13.6 | 否 |
| `notesOut` | 票據與可轉債未償餘額 | US$bn | 16.6 | 否 |
| `sharesA` | A 股流通股數 | bn 股 | 0.458872 | 否 |
| `sharesB` | B 股流通股數 | bn 股 | 0.0926649 | 否 |
| `sharesOut` | 流通股數合計 | bn 股 | 0.551537 | 是 |
| `basicWaso` | 加權平均流通股數 | bn 股 | 0.551 | 否 |
| `capexQ2` | 當季資本支出 | US$bn | 9.352 | 是 |
| `capexH1` | 上半年資本支出 | US$bn | 16.139 | 是 |
| `cashCapexH1` | 上半年現金購置固定資產 | US$bn | 14.117 | 否 |
| `cfoH1` | 上半年營運現金流 | US$bn | 3.663 | 否 |
| `cashInterestH1` | 上半年現金利息 | US$bn | 0.806 | 否 |
| `capInterestH1` | 上半年資本化利息 | US$bn | 0.176 | 否 |
| `deferredTotal` | 遞延收入合計 | US$bn | 9.692 | 是 |
| `deferredIn` | 上半年遞延收入淨流入 | US$bn | 1.365 | 是 |
| `ppe` | 固定資產毛額 | US$bn | 46.736 | 否 |
| `cip` | 在建工程 | US$bn | 11.9 | 否 |
| `rouOp` | 營業租賃使用權資產 | US$bn | 16.595 | 否 |
| `opLeaseLiab` | 營業租賃負債 | US$bn | 16.319 | 是 |
| `finLeaseLiab` | 融資租賃負債 | US$bn | 0.221 | 否 |
| `onBalanceUndiscounted` | 已入帳租約未折現付款 | US$bn | 29.37 | 是 |
| `offBalanceLease` | 未起租租約（表外） | US$bn | 35.5 | 是 |
| `singleSiteCap` | 單一站點租金上限 | US$bn | 14.7 | 是 |
| `singleSiteMw` | 該站點未交付 MW | MW | 393 | 否 |
| `constructionCostMw` | 按造價計租的未交付 MW | MW | 355 | 否 |
| `equipCommitLo` | 設備採購承諾下緣 | US$bn | 0.5 | 否 |
| `equipCommitHi` | 設備採購承諾上緣 | US$bn | 1.2 | 否 |
| `jvCommit` | JV 承諾出資上限 | US$bn | 1.7 | 否 |
| `jvPaidH1` | 上半年已付 JV 出資 | US$bn | 0.55 | 否 |
| `vieExposure` | 可變利益實體（VIE）最大曝險 | US$bn | 0.108 | 否 |
| `rouObtainedH1` | 上半年新取得使用權資產 | US$bn | 8.359 | 否 |
| `leaseCashH1` | 上半年租賃現金支付 | US$bn | 0.748 | 否 |
| `custA` | 最大客戶營收占比 | 比例 | 0.36 | 否 |
| `custB` | 第二大客戶營收占比 | 比例 | 0.26 | 否 |
| `custC` | 第三大客戶營收占比 | 比例 | 0.1 | 否 |
| `debtIssuedH1` | 上半年借款 | US$bn | 16.747 | 否 |
| `debtRepaidH1` | 上半年還款 | US$bn | 5.219 | 否 |
| `equityH1` | 上半年股權募資 | US$bn | 2.982 | 否 |

### `callFacts`：法說會與期後事項

換公司：全部必改（公司特有資料）。「程式使用」為否的欄位只是存檔備查，畫面與 Excel 的說明文字目前另外寫在程式裡。

| 欄位 | 意義 | 單位 | 目前數值 | 程式使用 |
|---|---|---|---|---|
| `activeGw` | 主動電力 | GW | 1.5 | 否 |
| `activeAddQ2` | 當季新增主動電力 | MW | 500 | 是 |
| `juneAddMw` | 季末月單月新增 | MW | 300 | 否 |
| `contractedGw` | 簽約電力（法說日） | GW | 4.2 | 是 |
| `contractedGwQ2` | 簽約電力（季末） | GW | 3.7 | 否 |
| `poweredLandGw` | 已取得電力的土地／選擇權／意向書 | GW | 1.5 | 否 |
| `yeActiveGw` | 年底主動電力指引 | GW | 1.85 | 是 |
| `gw2030` | 2030 年電力目標 | GW | 8 | 否 |
| `dataCenters` | 資料中心數 | 座 | 51 | 否 |
| `capexLo` | 全年資本支出指引下緣 | US$bn | 35 | 是 |
| `capexHi` | 全年資本支出指引上緣 | US$bn | 39 | 是 |
| `q3CapexLo` | 下一季資本支出指引下緣 | US$bn | 11.5 | 否 |
| `q3CapexHi` | 下一季資本支出指引上緣 | US$bn | 13.5 | 否 |
| `q3IntLo` | 下一季利息指引下緣 | US$bn | 0.86 | 否 |
| `q3IntHi` | 下一季利息指引上緣 | US$bn | 0.94 | 否 |
| `revLo` | 全年營收指引下緣 | US$bn | 12.4 | 否 |
| `revHi` | 全年營收指引上緣 | US$bn | 13.2 | 否 |
| `q3RevLo` | 下一季營收指引下緣 | US$bn | 3.45 | 是 |
| `q3RevHi` | 下一季營收指引上緣 | US$bn | 3.6 | 是 |
| `adjOpLo` | 全年調整後營業利益指引下緣 | US$bn | 0.96 | 否 |
| `adjOpHi` | 全年調整後營業利益指引上緣 | US$bn | 1.15 | 否 |
| `q3AdjOpLo` | 下一季調整後營業利益指引下緣 | US$bn | 0.2 | 否 |
| `q3AdjOpHi` | 下一季調整後營業利益指引上緣 | US$bn | 0.26 | 否 |
| `arrLo` | 期末年化經常性收入（ARR）指引下緣 | US$bn | 18.5 | 否 |
| `arrHi` | 期末 ARR 指引上緣 | US$bn | 19.5 | 否 |
| `q3NewCommit` | 季末後新增承諾 | US$bn | 25 | 否 |
| `priceUp` | 新約漲價幅度 | 比例 | 0.25 | 否 |
| `marginStep` | 新約貢獻率提升 | 文字 | 5–10 pt | 否 |
| `backlogStarted` | backlog 中已開始交付的比例（法說「>50%」） | 比例 | 0.5 | 否 |
| `inferenceArr` | 推論服務 ARR（年底） | US$bn | 0.25 | 否 |
| `otherArr` | 其他服務 ARR | US$bn | 0.4 | 否 |
| `convert` | 期後可轉債發行額 | US$bn | 3.7 | 否 |
| `convertNet` | 期後可轉債淨額 | US$bn | 3.6 | 否 |
| `convertCoupon` | 期後可轉債票面利率 | 比例 | 0.02875 | 否 |
| `convertPx` | 轉換價 | US$ | 97.85 | 否 |
| `atmShares` | 股權分銷（ATM）上限 | m 股 | 35 | 否 |
| `price0917` | 9/17 收盤價 | US$ | 79.88 | 是 |
| `tier34Active` | 主動電力位於 Tier 3/4 市場比例 | 比例 | 0.25 | 否 |
| `tier34Contracted` | 簽約電力位於 Tier 3/4 市場比例 | 比例 | 0.74 | 否 |
| `cdsMid` | CDS 中價 | bps | 720 | 否 |
| `cdsBidAsk` | CDS 買／賣價 | 文字 | 690 / 750 | 否 |
| `cdsRange` | CDS 近期區間 | 文字 | 680–855 | 否 |
| `cdsPeak` | CDS 峰值 | bps | 855 | 否 |
| `cdsPeakDate` | CDS 峰值日期 | 日期 | 2026-07-28 | 否 |
| `cdsLow` | CDS 低點 | bps | 452 | 否 |
| `cdsLowDate` | CDS 低點日期 | 日期 | 2026-06 | 否 |
| `availability` | 未動用信用額度 | US$bn | 10.014 | 否 |
| `price0918` | 9/18 收盤價 | US$ | 80.2 | 否 |
| `priceLast` | 最新收盤價 | US$ | 90.13 | 是 |
| `priceDate` | 最新收盤價日期 | 日期 | 2026-09-24 | 是 |
| `q3ShortDated` | 期後公告摘要 | 文字 | 2026-09-16 公告：6/30 後持續以更高價… | 否 |
| `ttmRev` | 近十二個月營收 | US$bn | 7.59 | 是 |
| `ttmOpInc` | 近十二個月 GAAP 營業損益 | US$bn | -0.231 | 是 |
| `ttmDa` | 近十二個月折舊攤銷 | US$bn | 3.991 | 是 |
| `ttmOpLease` | 近十二個月營業租賃成本 | US$bn | 1.377 | 否 |
| `mktCapLast` | CRWV 市值（Comps 用；與同業同一收盤日 peers.priceDate，v4.3 起不隨現價更新） | US$bn | 47.12 | 是 |
| `nextEarn` | 下次財報時間 | 文字 | 2026-11 (10-Q 期限 11/16) | 否 |

### `scenarios`：三個擴張情境

| 欄位 | 意義 | 單位 | 目前數值 | 換公司 |
|---|---|---|---|---|
| `scenarios.labels.low` | 保守情境名稱（空格前的文字會當作情境簡稱） | 文字 | 保守 4.2 GW | 必改 |
| `scenarios.labels.base` | 基準情境名稱 | 文字 | 基準 5.6 GW | 必改 |
| `scenarios.labels.high` | 積極情境名稱 | 文字 | 積極 8 GW | 必改 |
| `scenarios.accepted.low` | 保守情境：五期（FY26 下半年、FY27、FY28、FY29、FY30）各期末已驗收的主動電力 | MW 清單 | 1850、3100、3800、4200、4200 | 必改 |
| `scenarios.accepted.base` | 基準情境：同上 | MW 清單 | 1850、3100、4000、4800、5600 | 必改 |
| `scenarios.accepted.high` | 積極情境：同上 | MW 清單 | 1850、3100、4600、6300、8000 | 必改 |
| `scenarios.billableRatio.billable` | 計算「可計費 ÷ 已驗收」爬坡比例用的可計費 MW（與下一欄逐期相除） | MW 清單 | 1700、2900、4300、5900、7500 | 檢查 |
| `scenarios.billableRatio.accepted` | 同上，分母的已驗收 MW | MW 清單 | 1850、3100、4600、6300、8000 | 檢查 |
| `scenarios.leaseHighPath` | 積極情境下，尚未起租租約的新增年租金路徑；其他情境依 MW 比例縮放 | US$bn 清單 | 0.3、1.6、3、4、4.6 | 檢查 |
| `scenarios.leaseRampFloorMw` | 低於此電力時不產生新增表外租金（縮放公式的起點） | MW | 1500 | 檢查 |
| `scenarios.mw31.low` | 保守情境：模型期後一年（FY31）新增的 MW，用於 FY30 的預建支出 | MW | 0 | 檢查 |
| `scenarios.mw31.base` | 基準情境：同上 | MW | 500 | 檢查 |
| `scenarios.mw31.high` | 積極情境：同上 | MW | 1000 | 檢查 |
| `scenarios.capexTemplate.costMW` | 每 MW 建置成本（GPU＋網路＋機房內裝），各期 | US$m/MW 清單 | 34、34、34、34、34 | 檢查 |
| `scenarios.capexTemplate.customerFund` | 客戶預付占資本支出的比例，各期 | 比例清單 | 0.08、0.08、0.08、0.08、0.08 | 檢查 |
| `scenarios.capexTemplate.div` | JV 後續增資與策略投資，各期 | US$bn 清單 | 0.1、0.4、0.3、0.2、0.2 | 檢查 |

### `legacy`：舊版對照值

| 欄位 | 意義 | 單位 | 目前數值 | 換公司 |
|---|---|---|---|---|
| `legacy.capexV14` | 舊版（v1.4）手動資本支出，只供畫面對照 | US$bn 清單 | 21、45、50、50、45 | 可沿用 |
| `legacy.interestV14` | 舊版（v1.4）手動利息，只供畫面對照 | US$bn 清單 | 1.8、2.7、2.3、2、1.8 | 可沿用 |

### `defaults`：預設假設（畫面上可調的輸入）

| 欄位 | 意義 | 單位 | 目前數值 | 換公司 |
|---|---|---|---|---|
| `defaults.scenario` | 開啟時的預設情境（low／base／high） | 文字 | base | 檢查 |
| `defaults.lambda` | 提前支出比例：次年才上線的 MW，其建置支出落在前一年的比例 | 比例 | 0.35 | 檢查 |
| `defaults.mwYE25` | 上一年底主動電力（第一期期初） | MW | 850 | 必改 |
| `defaults.mw31` | 模型期後一年新增 MW 的預設值（情境切換時改用 scenarios.mw31） | MW | 500 | 檢查 |
| `defaults.capexFloor26` | 第一年資本支出下限（已下單的承諾，取公司指引下緣） | US$bn | 35 | 必改 |
| `defaults.gpuLife` | GPU 經濟壽命（決定汰換時點與折舊） | 年 | 6 | 檢查 |
| `defaults.revScale` | 每 MW 年收入整體倍數（反向 DCF 與壓力測試用，1＝不調整） | 倍 | 1 | 可沿用 |
| `defaults.capexScale` | 每 MW 建置成本整體倍數（1＝不調整） | 倍 | 1 | 可沿用 |
| `defaults.ebStart` | 第一期 EBITDA 率 | 比例 | 0.59 | 必改 |
| `defaults.ebSteady` | 最後一期（穩態）EBITDA 率；中間各期線性內插 | 比例 | 0.65 | 檢查 |
| `defaults.services` | 非算力服務營收（軟體、儲存等），各期 | US$bn 清單 | 0.3、1、1.8、2.8、3.8 | 檢查 |
| `defaults.debtBacklog` | 新債上限：總債務不超過 backlog 的倍數 | 倍 | 1 | 檢查 |
| `defaults.ctrTerm` | 新簽合約的平均年期（決定 backlog 補入量） | 年 | 5 | 檢查 |
| `defaults.minCash` | 最低現金：每期融資後期末現金不低於此值 | US$bn | 2 | 檢查 |
| `defaults.eqPx` | 新股發行參考價（預設＝現價） | US$ | 90.13 | 必改 |
| `defaults.eqDisc` | 新股發行折價 | 比例 | 0.1 | 檢查 |
| `defaults.eqCapPct` | 每年股權募資上限（占現市值）；輸入 9 以上視為無上限 | 比例 | 0.2 | 檢查 |
| `defaults.junkRate` | 股權上限用完後的高息債利率 | 比例 | 0.12 | 檢查 |
| `defaults.mwYE23` | 兩年前年底主動電力（推算車隊折舊用） | MW | 100 | 必改 |
| `defaults.mwYE24` | 一年前年底主動電力 | MW | 360 | 必改 |
| `defaults.ppe630` | 最新季末固定資產毛額 | US$bn | 46.736 | 必改 |
| `defaults.jvCommit` | 已承諾的 JV 出資餘額，各期 | US$bn 清單 | 1.15、0、0、0、0 | 必改 |
| `defaults.intCal` | 第一期利息校準值（讓模型利息對上公司季度指引） | US$bn | 0.35 | 必改 |
| `defaults.rpoFy26` | 最新季末 RPO | US$bn | 103.7 | 必改 |
| `defaults.rpoQ1Add` | 季末後新簽、尚未進 RPO 的承諾 | US$bn | 25 | 必改 |
| `defaults.rp` | RPO 在模型期內認列的比例（百分點；應與 rpo.scheduledShare 一致） | % | 84 | 必改 |
| `defaults.cash` | 最新季末現金（第一期期初現金） | US$bn | 5.5 | 必改 |
| `defaults.includeDebt` | 是否依到期表攤還既有債務（true＝是；false＝假設全數再融資） | 是／否 | 是 | 可沿用 |
| `defaults.includeAtm` | 是否計入期後股權／可轉債募資 | 是／否 | 是 | 可沿用 |
| `defaults.atm` | 期後股權／可轉債募資淨額（記在第一期） | US$bn | 6.2 | 必改 |
| `defaults.overlay` | 電力／維護成本另計（預設關；EBITDA 率已含電費，開啟會重複扣除） | 是／否 | 否 | 可沿用 |
| `defaults.cdsLink` | CDS 利差是否傳入新債利率（預設關） | 是／否 | 否 | 可沿用 |
| `defaults.linkSites` | 具名站點的 MW 是否連動第一期產能下限 | 是／否 | 是 | 可沿用 |
| `defaults.linkLeaseTail` | 舊模板遺留開關，目前程式未使用 | 是／否 | 是 | 可沿用 |
| `defaults.useAvgMw` | 收入以平均在役 MW 計（true）或期末存量計（false） | 是／否 | 是 | 可沿用 |
| `defaults.billableOpen` | 最新季末可計費 MW（第一期期初） | MW | 1350 | 必改 |
| `defaults.cds` | 信用違約交換（CDS）中價 | bps | 720 | 必改 |
| `defaults.cdsBid` | CDS 買價 | bps | 690 | 必改 |
| `defaults.cdsAsk` | CDS 賣價 | bps | 750 | 必改 |
| `defaults.cdsLo` | CDS 近期區間下緣 | bps | 680 | 必改 |
| `defaults.cdsHi` | CDS 近期區間上緣 | bps | 855 | 必改 |
| `defaults.cdsDate` | CDS 報價日期與來源標記 | 文字 | 2026-09（User-provided 報價） | 必改 |
| `defaults.useFacility` | 融資時是否先動用未動用信用額度 | 是／否 | 是 | 可沿用 |
| `defaults.facility` | 未動用信用額度 | US$bn | 10 | 必改 |
| `defaults.m.accepted` | 已驗收 MW 的預設路徑（實際依所選情境覆寫） | MW 清單 | 1850、3100、4000、4800、5600 | 檢查 |
| `defaults.m.billable` | 可計費 MW 的預設路徑（實際依情境與爬坡比例覆寫） | MW 清單 | 1700、2900、3739、4495、5250 | 檢查 |
| `defaults.m.util` | 利用率，各期 | % 清單 | 95、95、94、93、92 | 檢查 |
| `defaults.m.revMW` | 每 MW 年收入，各期 | US$bn/MW 清單 | 0.0112、0.0115、0.0115、0.011、0.0105 | 必改 |
| `defaults.m.aiShare` | AI 占比，各期（目前只做範圍檢查，未參與計算） | % 清單 | 100、100、100、100、100 | 可沿用 |
| `defaults.m.fill` | 新產能簽約率：未被既有 RPO 占用的產能能賣出的比例 | % 清單 | 100、100、90、85、80 | 檢查 |
| `defaults.m.power` | 電價（overlay 開啟時才用） | $/MWh 清單 | 60、62、64、66、68 | 檢查 |
| `defaults.m.pue` | 電力使用效率 PUE（overlay 用） | 倍 清單 | 1.25、1.24、1.22、1.2、1.2 | 檢查 |
| `defaults.m.maint` | 維護成本（overlay 用） | US$m/MW 清單 | 0.15、0.15、0.16、0.16、0.17 | 檢查 |
| `defaults.m.defaultP` | 客戶違約率 | % 清單 | 0.5、1、1.5、2、2.5 | 檢查 |
| `defaults.m.recovery` | 違約回收率 | % 清單 | 50、50、50、50、50 | 檢查 |
| `defaults.m.rate` | 新債利率 | % 清單 | 9、9、9、9、9 | 檢查 |
| `defaults.terminal.residual` | 模型期末 GPU 殘值率 | % | 25 | 檢查 |
| `defaults.terminal.rerent` | 期末設備再出租率 | % | 75 | 檢查 |
| `defaults.terminal.margin` | 模型期後剩餘 RPO 的利潤率 | % | 40 | 檢查 |
| `defaults.terminal.residualLeaseYears` | 模型期後租約剩餘年數 | 年 | 12 | 檢查 |
| `defaults.sites` | 具名資料中心站點，一站一列。欄位：id 代碼、name 名稱、operator 房東／合作方、planned 契約 MW、energized 已通電 MW、accepted 已驗收 MW、billable 可計費 MW、contract 合約總值（US$bn，可無）、years 合約年期（可無）、status 狀態說明、next 下一里程碑、date 預計時間、confidence 信心（高／中／低） | 清單 | 6 筆 | 必改 |

### `valuation`：評價參數

| 欄位 | 意義 | 單位 | 目前數值 | 換公司 |
|---|---|---|---|---|
| `valuation.price` | 現價 | US$ | 90.13 | 必改 |
| `valuation.shares` | 評價股數（含期後股權發行上限） | bn 股 | 0.587 | 必改 |
| `valuation.netDebt` | 淨負債（最新季末本金 − 現金） | US$bn | 30 | 必改 |
| `valuation.tax` | 稅率 | 比例 | 0.21 | 檢查 |
| `valuation.nol` | 期初可扣抵虧損（NOL） | US$bn | 4 | 必改 |
| `valuation.wacc` | 加權平均資金成本 WACC | 比例 | 0.11 | 檢查 |
| `valuation.g` | 永續成長率 | 比例 | 0.03 | 檢查 |
| `valuation.sbc` | 年度股份基礎薪酬 | US$bn | 0.7 | 必改 |
| `valuation.maintRatio` | 終值的維持性資本支出占折舊比例 | 比例 | 0.8 | 檢查 |
| `valuation.evEbitda` | EV/EBITDA 倍數 | 倍 | 6 | 檢查 |
| `valuation.evYear` | EV/EBITDA 錨定年度（1＝FY27 … 4＝FY30） | 年度代碼 | 3 | 檢查 |
| `valuation.dcfMode` | DCF 股權為負時的處理：zero＝0 截斷、option＝選擇權法 | 文字 | zero | 可沿用 |
| `valuation.sigma` | 企業價值波動率（選擇權法用） | 比例 | 0.5 | 檢查 |
| `valuation.rf` | 無風險利率（選擇權法用） | 比例 | 0.04 | 檢查 |
| `valuation.optT` | 選擇權期間（至模型期末） | 年 | 4.5 | 檢查 |

### `methodology`：評價方法與評等門檻

| 欄位 | 意義 | 單位 | 目前數值 | 換公司 |
|---|---|---|---|---|
| `methodology.blendWeights.dcf` | 加權目標價中 DCF 的權重 | 比例 | 0.45 | 可沿用 |
| `methodology.blendWeights.pe` | 加權目標價中 EV/EBITDA 的權重（兩者合計 1） | 比例 | 0.55 | 可沿用 |
| `methodology.rangeMultiples` | 方法區間的 EV/EBITDA 倍數下端與上端 | 倍 清單 | 5、6 | 檢查 |
| `methodology.consensusGapTol` | 與市場共識比較的判斷句門檻：營收、EBITDA、CapEx 差距絕對值超過此比例即視為分歧（v4.3） | 比例 | 0.05 | 可沿用 |
| `methodology.rating.buyUpsideMin` | 買進：空間（加權目標價 ÷ 現價 − 1）至少要達到的值 | 比例 | 0.25 | 可沿用 |
| `methodology.rating.buyTvShareMax` | 買進：終值占企業價值須低於此值 | 比例 | 0.9 | 可沿用 |
| `methodology.rating.sellUpsideMax` | 賣出：空間小於或等於此值即賣出；賣出門檻價＝現價 ×（1＋此值） | 比例（負數） | -0.15 | 可沿用 |
| `methodology.rating.equityRaiseMaxMult` | 五期股權募資超過「現市值 × 此倍數」即禁止買進 | 倍 | 1.5 | 可沿用 |
| `methodology.rating.sellUpsideMaxIfEquityOver` | 股權募資超標時，空間小於或等於此值即賣出 | 比例（負數） | -0.08 | 可沿用 |
| `methodology.rating.sellMarginAlert` | 任一情境與賣出門檻的距離小於「現價 × 此值」時，判斷句另外揭露 | 比例 | 0.05 | 可沿用 |
| `methodology.rating.tvShareWarn` | 終值占企業價值超過此值時提出警示（融資說明、檢查頁） | 比例 | 0.85 | 可沿用 |

### `peers`：同業比較（Comps）

| 欄位 | 意義 | 單位 | 目前數值 | 換公司 |
|---|---|---|---|---|
| `peers.priceDate` | 同業市值的收盤日 | 日期 | 2026-09-21 | 必改 |
| `peers.priceSource` | 同業市值來源 | 文字 | S&P Global via stockanalys… | 必改 |
| `peers.list` | 同業，一家一列（HTML Comps 分頁與 Excel「可比公司」頁共用）。欄位：ticker 代號、name 公司名、labelHtml／labelXlsx 兩邊顯示的名稱、roleHtml 定位說明（HTML）、mkt 市值、netDebt 淨負債、rev 近十二個月營收、opl 營業租賃負債、opInc GAAP 營業損益、da 折舊攤銷（以上 US$bn）、asOf 資料期、noteHtml／noteXlsx 兩邊的備註。EV＝市值＋淨負債、EBITDA＝營業損益＋折舊攤銷，由程式計算 | 清單 | 4 筆 | 必改 |
| `peers.textHtml.headerTip` | HTML Comps 表標題的浮動說明 | 文字 | 市值為 2026-09-21 收盤（S&P Glob… | 必改 |
| `peers.textHtml.readingTip` | HTML「讀法」段落的浮動說明（折價來源） | 文字 | 這個折價有三個來源，不能全部解讀為便宜：(1) 分母… | 必改 |
| `peers.textHtml.caveat` | HTML Comps 表下方的「口徑與限制」 | 文字 | 口徑與限制：市值為 2026-09-21 收盤，負債… | 必改 |
| `peers.textXlsx.subtitle` | Excel「可比公司」頁第 2 列說明 | 文字 | EV＝市值＋（有息負債−非受限現金）；含租賃＝EV＋… | 必改 |
| `peers.textXlsx.notes` | Excel「可比公司」頁表下方的讀法說明（每句一列） | 文字清單 | 讀法：CRWV 的 TTM EV/Sales 約為同…、(2) CRWV 用租約取得機房，加入營業租賃負債後…、前瞻：NBIS 前瞻 EV/Sales 約 9.3x… | 必改 |

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
| `peers` | dict（v4.2） |

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
「來源」頁與站點說明、法說對照表等長文字（同業市值與賣方目標價的來源引用句已於 v4.3 改讀 company.json 與共識檔），以及 `latestQuarter`／`callFacts` 中「程式使用：否」的數字在畫面上的文字寫法。換公司時仍需手動改這些地方。同業 Comps 與評等門檻已於 v4.2 移入（`peers`、`methodology.rating`）。

### v4.0 核對工具
- `load_engine.js`：在 node 載入 company.json＋segA＋segB（cmp31.js 使用）。
- `xl_diff.py a.xlsx b.xlsx [--values]`：Excel 逐格比對（公式或重算後的值）。
- `crawl.py <html> <out.json>`：逐頁逐分頁擷取畫面文字，用於比對兩版 HTML 的顯示是否相同。2026-09-25 修正：原本只擷取第一個 `<main>`（資金模型頁的一個區塊），總結頁與損益與評價頁的內容、以及多數次級分頁實際上沒有被比對；現改為擷取整頁可見文字並逐一展開兩層選單（v4.0 為 32 個視圖、約 111,000 字）。
- 結構性修改的驗收標準：cmp31 三情境全數一致；crawl 比對除版本紀錄外 0 差異；xl_diff 除版本紀錄外 0 差異（v4.2 起有新增列時用 `--by-label`）。
