# v4.2：產生 README「company.json 欄位說明」的表格。意義、單位、換公司時的處理寫在下方；「目前數值」與「程式使用」直接讀 company.json 與程式碼。
# company.json 有欄位沒寫說明、或說明了不存在的欄位，都直接報錯——新增欄位時先在這裡補說明，再重新產生。
# 用法：python3 scripts/fields_doc.py > out/fields.md，把輸出貼回 README「company.json 欄位說明」的各區表格。
import json, sys, re, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CO = json.load(open(os.path.join(REPO, 'company.json'), encoding='utf-8'))
CODE = ''.join(open(f'{REPO}/{f}', encoding='utf-8').read() for f in
               ['segA.js', 'segB.js', 'segC.js', 'segD.js', 'segE.js', 'tail.js', 'build_xlsx.py', 'cmp31.js'])
P5 = '五期（FY26 下半年、FY27、FY28、FY29、FY30）'
M, C, K = '必改', '檢查', '可沿用'   # 換公司：必改＝公司特有資料；檢查＝判斷值，依新公司重新評估；可沿用＝口徑或方法，通常不必改

# (路徑, 意義, 單位, 換公司)
F = [
 ('meta.company', '公司名稱', '文字', M), ('meta.ticker', '股票代號', '文字', M),
 ('meta.updateDate', '資料更新日', '日期', M), ('meta.priceDate', '股價日期（現價的收盤日；畫面與 Excel 的現價日期都讀這格）', '日期', M),
 ('meta.consensusFile', '市場共識資料檔路徑（v4.3；只讀，由使用者查證後提供；建置時併入 HTML、Excel 讀同一檔）', '路徑', M),
 ('meta.sourceOrderNote', '資料來源的先後與衝突時的取捨原則（畫面說明文字）', '文字', M),
 ('periods', '模型期的名稱，共 5 期', '文字清單', C),
 ('periodYears', '每一期的長度；第一期是半年，所以是 0.5', '年', C),
 ('actual1H.label', '「上半年實際數」的標題', '文字', M),
 ('actual1H.cash1231', '上一年底現金', 'US$bn', M), ('actual1H.revenue', '上半年營收', 'US$bn', M),
 ('actual1H.capex', '上半年資本支出（認列口徑，含設備商融資）', 'US$bn', M),
 ('actual1H.cashCapex', '上半年現金購置固定資產', 'US$bn', M), ('actual1H.interest', '上半年利息費用', 'US$bn', M),
 ('actual1H.leasePaid', '上半年租賃現金支付', 'US$bn', M), ('actual1H.debtRepaid', '上半年還款', 'US$bn', M),
 ('actual1H.borrow', '上半年借款', 'US$bn', M), ('actual1H.equity', '上半年股權募資', 'US$bn', M),
 ('actual1H.cappedCall', '上半年 capped call（可轉債配套避險）支出', 'US$bn', M),
 ('actual1H.jv', '上半年合資（JV）與策略投資出資', 'US$bn', M), ('actual1H.cfo', '上半年營運現金流', 'US$bn', M),
 ('actual1H.prepay', '上半年客戶預付（遞延收入淨流入）', 'US$bn', M), ('actual1H.da', '上半年折舊攤銷', 'US$bn', M),
 ('actual1H.sbc', '上半年股份基礎薪酬', 'US$bn', M), ('actual1H.opInc', '上半年 GAAP 營業損益', 'US$bn', M),
 ('actual1H.ni', '上半年淨損益', 'US$bn', M), ('actual1H.eps', '上半年 GAAP 每股盈餘', 'US$', M),
 ('actual1H.ngEps', '上半年每股盈餘（加回股份基礎薪酬）', 'US$', M),
 ('actual1H.adjEbitda', '上半年調整後 EBITDA（v4.3；只用於與市場共識比較 FY26，不進模型損益與評價）', 'US$bn', M),
 ('actual1H.adjEbitdaMeta', '上述數字的 Q1／Q2 拆分、來源、標記與備註（建置時檢查 Q1＋Q2＝合計）', '物件', M),
 ('historicalPL', '歷年損益，一年一列（損益頁的歷史欄）。每列欄位：year 年度、revenue 營收、opInc GAAP 營業損益、ni 淨損益（以上 US$bn）、eps GAAP 每股盈餘、ngEps 加回股份基礎薪酬的每股盈餘（US$）、shares 加權流通股數（bn）、tag 來源標記', '清單', M),
 ('rpo.scheduledShare', '剩餘履約義務（RPO，已簽約未認列的營收）預計在模型期內認列的比例', '比例', M),
 ('rpo.bucketWeights', f'RPO 在{P5}各期認列的比例，合計等於上一欄', '比例清單', M),
 ('leases.onBalanceCash', f'已入帳租約在{P5}各期的現金租金', 'US$bn 清單', M),
 ('leases.afterFY30', '已入帳租約在模型期之後還要付的租金合計', 'US$bn', M),
 ('leases.facts.onBal', '已入帳租約未折現付款合計', 'US$bn', M),
 ('leases.facts.notCommenced', '已簽約但尚未起租的租約（表外）', 'US$bn', M),
 ('leases.facts.singleCap', '單一大型站點的租金上限（10-Q 揭露）', 'US$bn', M),
 ('leases.facts.share', '第三方租賃占機房取得的比例（用於租金基準檢驗）', '比例', C),
 ('leases.operatingPayments', '營業租賃到期表：五期各期，最後一格為之後合計（Excel 租賃頁）', 'US$bn 清單', M),
 ('leases.financePayments', '融資租賃到期表：同上格式', 'US$bn 清單', M),
 ('debt.amortization', f'既有債務在{P5}各期的排程還本', 'US$bn 清單', M),
 ('debt.amortAfterFY30', '模型期之後的還本合計', 'US$bn', M),
 ('debt.instruments', '既有債務逐筆明細，一筆一列：[名稱, 追索／非追索, 到期, 有效利率（比例）, 本金（US$bn）, 備註]。加總本金須等於 10-Q 本金合計', '清單', M),
 ('debt.convertible.principal', '期後新發行可轉債本金（不在五期還本表內，只計利息）', 'US$bn', M),
 ('debt.convertible.coupon', '該可轉債票面利率', '比例', M),
 ('scenarios.labels.low', '保守情境名稱（空格前的文字會當作情境簡稱）', '文字', M),
 ('scenarios.labels.base', '基準情境名稱', '文字', M), ('scenarios.labels.high', '積極情境名稱', '文字', M),
 ('scenarios.accepted.low', f'保守情境：{P5}各期末已驗收的主動電力', 'MW 清單', M),
 ('scenarios.accepted.base', '基準情境：同上', 'MW 清單', M), ('scenarios.accepted.high', '積極情境：同上', 'MW 清單', M),
 ('scenarios.billableRatio.billable', '計算「可計費 ÷ 已驗收」爬坡比例用的可計費 MW（與下一欄逐期相除）', 'MW 清單', C),
 ('scenarios.billableRatio.accepted', '同上，分母的已驗收 MW', 'MW 清單', C),
 ('scenarios.leaseHighPath', '積極情境下，尚未起租租約的新增年租金路徑；其他情境依 MW 比例縮放', 'US$bn 清單', C),
 ('scenarios.leaseRampFloorMw', '低於此電力時不產生新增表外租金（縮放公式的起點）', 'MW', C),
 ('scenarios.mw31.low', '保守情境：模型期後一年（FY31）新增的 MW，用於 FY30 的預建支出', 'MW', C),
 ('scenarios.mw31.base', '基準情境：同上', 'MW', C), ('scenarios.mw31.high', '積極情境：同上', 'MW', C),
 ('scenarios.capexTemplate.costMW', '每 MW 建置成本（GPU＋網路＋機房內裝），各期', 'US$m/MW 清單', C),
 ('scenarios.capexTemplate.customerFund', '客戶預付占資本支出的比例，各期', '比例清單', C),
 ('scenarios.capexTemplate.div', 'JV 後續增資與策略投資，各期', 'US$bn 清單', C),
 ('legacy.capexV14', '舊版（v1.4）手動資本支出，只供畫面對照', 'US$bn 清單', K),
 ('legacy.interestV14', '舊版（v1.4）手動利息，只供畫面對照', 'US$bn 清單', K),
 ('defaults.scenario', '開啟時的預設情境（low／base／high）', '文字', C),
 ('defaults.lambda', '提前支出比例：次年才上線的 MW，其建置支出落在前一年的比例', '比例', C),
 ('defaults.mwYE25', '上一年底主動電力（第一期期初）', 'MW', M),
 ('defaults.mw31', '模型期後一年新增 MW 的預設值（情境切換時改用 scenarios.mw31）', 'MW', C),
 ('defaults.capexFloor26', '第一年資本支出下限（已下單的承諾，取公司指引下緣）', 'US$bn', M),
 ('defaults.gpuLife', 'GPU 經濟壽命（決定汰換時點與折舊）', '年', C),
 ('defaults.revScale', '每 MW 年收入整體倍數（反向 DCF 與壓力測試用，1＝不調整）', '倍', K),
 ('defaults.capexScale', '每 MW 建置成本整體倍數（1＝不調整）', '倍', K),
 ('defaults.ebStart', '第一期 EBITDA 率', '比例', M), ('defaults.ebSteady', '最後一期（穩態）EBITDA 率；中間各期線性內插', '比例', C),
 ('defaults.services', '非算力服務營收（軟體、儲存等），各期', 'US$bn 清單', C),
 ('defaults.debtBacklog', '新債上限：總債務不超過 backlog 的倍數', '倍', C),
 ('defaults.ctrTerm', '新簽合約的平均年期（決定 backlog 補入量）', '年', C),
 ('defaults.minCash', '最低現金：每期融資後期末現金不低於此值', 'US$bn', C),
 ('defaults.eqPx', '新股發行參考價（預設＝現價）', 'US$', M),
 ('defaults.eqDisc', '新股發行折價', '比例', C),
 ('defaults.eqCapPct', '每年股權募資上限（占現市值）；輸入 9 以上視為無上限', '比例', C),
 ('defaults.junkRate', '股權上限用完後的高息債利率', '比例', C),
 ('defaults.mwYE23', '兩年前年底主動電力（推算車隊折舊用）', 'MW', M),
 ('defaults.mwYE24', '一年前年底主動電力', 'MW', M),
 ('defaults.ppe630', '最新季末固定資產毛額', 'US$bn', M),
 ('defaults.jvCommit', '已承諾的 JV 出資餘額，各期', 'US$bn 清單', M),
 ('defaults.intCal', '第一期利息校準值（讓模型利息對上公司季度指引）', 'US$bn', M),
 ('defaults.rpoFy26', '最新季末 RPO', 'US$bn', M),
 ('defaults.rpoQ1Add', '季末後新簽、尚未進 RPO 的承諾', 'US$bn', M),
 ('defaults.rp', 'RPO 在模型期內認列的比例（百分點；應與 rpo.scheduledShare 一致）', '%', M),
 ('defaults.cash', '最新季末現金（第一期期初現金）', 'US$bn', M),
 ('defaults.includeDebt', '是否依到期表攤還既有債務（true＝是；false＝假設全數再融資）', '是／否', K),
 ('defaults.includeAtm', '是否計入期後股權／可轉債募資', '是／否', K),
 ('defaults.atm', '期後股權／可轉債募資淨額（記在第一期）', 'US$bn', M),
 ('defaults.overlay', '電力／維護成本另計（預設關；EBITDA 率已含電費，開啟會重複扣除）', '是／否', K),
 ('defaults.cdsLink', 'CDS 利差是否傳入新債利率（預設關）', '是／否', K),
 ('defaults.linkSites', '具名站點的 MW 是否連動第一期產能下限', '是／否', K),
 ('defaults.linkLeaseTail', '舊模板遺留開關，目前程式未使用', '是／否', K),
 ('defaults.useAvgMw', '收入以平均在役 MW 計（true）或期末存量計（false）', '是／否', K),
 ('defaults.billableOpen', '最新季末可計費 MW（第一期期初）', 'MW', M),
 ('defaults.cds', '信用違約交換（CDS）中價', 'bps', M), ('defaults.cdsBid', 'CDS 買價', 'bps', M),
 ('defaults.cdsAsk', 'CDS 賣價', 'bps', M), ('defaults.cdsLo', 'CDS 近期區間下緣', 'bps', M),
 ('defaults.cdsHi', 'CDS 近期區間上緣', 'bps', M), ('defaults.cdsDate', 'CDS 報價日期與來源標記', '文字', M),
 ('defaults.useFacility', '融資時是否先動用未動用信用額度', '是／否', K),
 ('defaults.facility', '未動用信用額度', 'US$bn', M),
 ('defaults.m.accepted', '已驗收 MW 的預設路徑（實際依所選情境覆寫）', 'MW 清單', C),
 ('defaults.m.billable', '可計費 MW 的預設路徑（實際依情境與爬坡比例覆寫）', 'MW 清單', C),
 ('defaults.m.util', '利用率，各期', '% 清單', C), ('defaults.m.revMW', '每 MW 年收入，各期', 'US$bn/MW 清單', M),
 ('defaults.m.aiShare', 'AI 占比，各期（目前只做範圍檢查，未參與計算）', '% 清單', K),
 ('defaults.m.fill', '新產能簽約率：未被既有 RPO 占用的產能能賣出的比例', '% 清單', C),
 ('defaults.m.power', '電價（overlay 開啟時才用）', '$/MWh 清單', C), ('defaults.m.pue', '電力使用效率 PUE（overlay 用）', '倍 清單', C),
 ('defaults.m.maint', '維護成本（overlay 用）', 'US$m/MW 清單', C),
 ('defaults.m.defaultP', '客戶違約率', '% 清單', C), ('defaults.m.recovery', '違約回收率', '% 清單', C),
 ('defaults.m.rate', '新債利率', '% 清單', C),
 ('defaults.terminal.residual', '模型期末 GPU 殘值率', '%', C), ('defaults.terminal.rerent', '期末設備再出租率', '%', C),
 ('defaults.terminal.margin', '模型期後剩餘 RPO 的利潤率', '%', C),
 ('defaults.terminal.residualLeaseYears', '模型期後租約剩餘年數', '年', C),
 ('defaults.sites', '具名資料中心站點，一站一列。欄位：id 代碼、name 名稱、operator 房東／合作方、planned 契約 MW、energized 已通電 MW、accepted 已驗收 MW、billable 可計費 MW、contract 合約總值（US$bn，可無）、years 合約年期（可無）、status 狀態說明、next 下一里程碑、date 預計時間、confidence 信心（高／中／低）', '清單', M),
 ('valuation.price', '現價', 'US$', M), ('valuation.shares', '評價股數（含期後股權發行上限）', 'bn 股', M),
 ('valuation.netDebt', '淨負債（最新季末本金 − 現金）', 'US$bn', M), ('valuation.tax', '稅率', '比例', C),
 ('valuation.nol', '期初可扣抵虧損（NOL）', 'US$bn', M), ('valuation.wacc', '加權平均資金成本 WACC', '比例', C),
 ('valuation.g', '永續成長率', '比例', C), ('valuation.sbc', '年度股份基礎薪酬', 'US$bn', M),
 ('valuation.maintRatio', '終值的維持性資本支出占折舊比例', '比例', C),
 ('valuation.evEbitda', 'EV/EBITDA 倍數', '倍', C), ('valuation.evYear', 'EV/EBITDA 錨定年度（1＝FY27 … 4＝FY30）', '年度代碼', C),
 ('valuation.dcfMode', 'DCF 股權為負時的處理：zero＝0 截斷、option＝選擇權法', '文字', K),
 ('valuation.sigma', '企業價值波動率（選擇權法用）', '比例', C), ('valuation.rf', '無風險利率（選擇權法用）', '比例', C),
 ('valuation.optT', '選擇權期間（至模型期末）', '年', C),
 ('methodology.blendWeights.dcf', '加權目標價中 DCF 的權重', '比例', K),
 ('methodology.blendWeights.pe', '加權目標價中 EV/EBITDA 的權重（兩者合計 1）', '比例', K),
 ('methodology.rangeMultiples', '方法區間的 EV/EBITDA 倍數下端與上端', '倍 清單', C),
 ('methodology.consensusGapTol', '與市場共識比較的判斷句門檻：營收、EBITDA、CapEx 差距絕對值超過此比例即視為分歧（v4.3）', '比例', K),
 ('methodology.rating.buyUpsideMin', '買進：空間（加權目標價 ÷ 現價 − 1）至少要達到的值', '比例', K),
 ('methodology.rating.buyTvShareMax', '買進：終值占企業價值須低於此值', '比例', K),
 ('methodology.rating.sellUpsideMax', '賣出：空間小於或等於此值即賣出；賣出門檻價＝現價 ×（1＋此值）', '比例（負數）', K),
 ('methodology.rating.equityRaiseMaxMult', '五期股權募資超過「現市值 × 此倍數」即禁止買進', '倍', K),
 ('methodology.rating.sellUpsideMaxIfEquityOver', '股權募資超標時，空間小於或等於此值即賣出', '比例（負數）', K),
 ('methodology.rating.sellMarginAlert', '任一情境與賣出門檻的距離小於「現價 × 此值」時，判斷句另外揭露', '比例', K),
 ('methodology.rating.tvShareWarn', '終值占企業價值超過此值時提出警示（融資說明、檢查頁）', '比例', K),
 ('peers.priceDate', '同業市值的收盤日', '日期', M), ('peers.priceSource', '同業市值來源', '文字', M),
 ('peers.list', '同業，一家一列（HTML Comps 分頁與 Excel「可比公司」頁共用）。欄位：ticker 代號、name 公司名、labelHtml／labelXlsx 兩邊顯示的名稱、roleHtml 定位說明（HTML）、mkt 市值、netDebt 淨負債、rev 近十二個月營收、opl 營業租賃負債、opInc GAAP 營業損益、da 折舊攤銷（以上 US$bn）、asOf 資料期、noteHtml／noteXlsx 兩邊的備註。EV＝市值＋淨負債、EBITDA＝營業損益＋折舊攤銷，由程式計算', '清單', M),
 ('peers.textHtml.headerTip', 'HTML Comps 表標題的浮動說明', '文字', M),
 ('peers.textHtml.readingTip', 'HTML「讀法」段落的浮動說明（折價來源）', '文字', M),
 ('peers.textHtml.caveat', 'HTML Comps 表下方的「口徑與限制」', '文字', M),
 ('peers.textXlsx.subtitle', 'Excel「可比公司」頁第 2 列說明', '文字', M),
 ('peers.textXlsx.notes', 'Excel「可比公司」頁表下方的讀法說明（每句一列）', '文字清單', M),
]
LQ = {
 'filed': ('申報日', '日期'), 'periodEnd': ('季末日', '日期'), 'revenue': ('當季營收', 'US$bn'), 'yoy': ('當季營收年增率', '比例'),
 'h1Revenue': ('上半年營收', 'US$bn'), 'costRev': ('當季營收成本', 'US$bn'), 'techInfra': ('當季技術與基礎設施費用', 'US$bn'),
 'opInc': ('當季 GAAP 營業損益', 'US$bn'), 'interest': ('當季利息費用', 'US$bn'), 'h1Interest': ('上半年利息費用', 'US$bn'),
 'ni': ('當季淨損益', 'US$bn'), 'h1Ni': ('上半年淨損益', 'US$bn'), 'epsDiluted': ('當季稀釋每股盈餘', 'US$'),
 'sbc': ('當季股份基礎薪酬', 'US$bn'), 'da': ('當季折舊攤銷', 'US$bn'), 'adjEbitda': ('當季調整後 EBITDA', 'US$bn'),
 'adjOpInc': ('當季調整後營業利益', 'US$bn'), 'rpo': ('季末 RPO', 'US$bn'), 'backlog': ('季末 backlog（含其他）', 'US$bn'),
 'rpo24m': ('RPO 於 24 個月內認列比例', '比例'), 'rpo25to48': ('RPO 於 25–48 個月認列比例', '比例'),
 'rpo49to78': ('RPO 於 49–78 個月認列比例', '比例'), 'cash': ('季末現金', 'US$bn'), 'restricted': ('受限現金', 'US$bn'),
 'marketable': ('有價證券', 'US$bn'), 'availability': ('未動用信用額度', 'US$bn'), 'debtPrincipal': ('債務本金合計', 'US$bn'),
 'recourseNet': ('追索債務淨額', 'US$bn'), 'nonRecourseNet': ('非追索債務淨額', 'US$bn'), 'ddtlOut': ('DDTL 未償餘額', 'US$bn'),
 'notesOut': ('票據與可轉債未償餘額', 'US$bn'), 'sharesA': ('A 股流通股數', 'bn 股'), 'sharesB': ('B 股流通股數', 'bn 股'),
 'sharesOut': ('流通股數合計', 'bn 股'), 'basicWaso': ('加權平均流通股數', 'bn 股'), 'capexQ2': ('當季資本支出', 'US$bn'),
 'capexH1': ('上半年資本支出', 'US$bn'), 'cashCapexH1': ('上半年現金購置固定資產', 'US$bn'), 'cfoH1': ('上半年營運現金流', 'US$bn'),
 'cashInterestH1': ('上半年現金利息', 'US$bn'), 'capInterestH1': ('上半年資本化利息', 'US$bn'), 'deferredTotal': ('遞延收入合計', 'US$bn'),
 'deferredIn': ('上半年遞延收入淨流入', 'US$bn'), 'ppe': ('固定資產毛額', 'US$bn'), 'cip': ('在建工程', 'US$bn'),
 'rouOp': ('營業租賃使用權資產', 'US$bn'), 'opLeaseLiab': ('營業租賃負債', 'US$bn'), 'finLeaseLiab': ('融資租賃負債', 'US$bn'),
 'onBalanceUndiscounted': ('已入帳租約未折現付款', 'US$bn'), 'offBalanceLease': ('未起租租約（表外）', 'US$bn'),
 'singleSiteCap': ('單一站點租金上限', 'US$bn'), 'singleSiteMw': ('該站點未交付 MW', 'MW'), 'constructionCostMw': ('按造價計租的未交付 MW', 'MW'),
 'equipCommitLo': ('設備採購承諾下緣', 'US$bn'), 'equipCommitHi': ('設備採購承諾上緣', 'US$bn'), 'jvCommit': ('JV 承諾出資上限', 'US$bn'),
 'jvPaidH1': ('上半年已付 JV 出資', 'US$bn'), 'vieExposure': ('可變利益實體（VIE）最大曝險', 'US$bn'),
 'rouObtainedH1': ('上半年新取得使用權資產', 'US$bn'), 'leaseCashH1': ('上半年租賃現金支付', 'US$bn'),
 'custA': ('最大客戶營收占比', '比例'), 'custB': ('第二大客戶營收占比', '比例'), 'custC': ('第三大客戶營收占比', '比例'),
 'debtIssuedH1': ('上半年借款', 'US$bn'), 'debtRepaidH1': ('上半年還款', 'US$bn'), 'equityH1': ('上半年股權募資', 'US$bn'),
}
CF = {
 'activeGw': ('主動電力', 'GW'), 'activeAddQ2': ('當季新增主動電力', 'MW'), 'juneAddMw': ('季末月單月新增', 'MW'),
 'contractedGw': ('簽約電力（法說日）', 'GW'), 'contractedGwQ2': ('簽約電力（季末）', 'GW'), 'poweredLandGw': ('已取得電力的土地／選擇權／意向書', 'GW'),
 'yeActiveGw': ('年底主動電力指引', 'GW'), 'gw2030': ('2030 年電力目標', 'GW'), 'dataCenters': ('資料中心數', '座'),
 'capexLo': ('全年資本支出指引下緣', 'US$bn'), 'capexHi': ('全年資本支出指引上緣', 'US$bn'),
 'q3CapexLo': ('下一季資本支出指引下緣', 'US$bn'), 'q3CapexHi': ('下一季資本支出指引上緣', 'US$bn'),
 'q3IntLo': ('下一季利息指引下緣', 'US$bn'), 'q3IntHi': ('下一季利息指引上緣', 'US$bn'),
 'revLo': ('全年營收指引下緣', 'US$bn'), 'revHi': ('全年營收指引上緣', 'US$bn'),
 'q3RevLo': ('下一季營收指引下緣', 'US$bn'), 'q3RevHi': ('下一季營收指引上緣', 'US$bn'),
 'adjOpLo': ('全年調整後營業利益指引下緣', 'US$bn'), 'adjOpHi': ('全年調整後營業利益指引上緣', 'US$bn'),
 'q3AdjOpLo': ('下一季調整後營業利益指引下緣', 'US$bn'), 'q3AdjOpHi': ('下一季調整後營業利益指引上緣', 'US$bn'),
 'arrLo': ('期末年化經常性收入（ARR）指引下緣', 'US$bn'), 'arrHi': ('期末 ARR 指引上緣', 'US$bn'),
 'q3NewCommit': ('季末後新增承諾', 'US$bn'), 'priceUp': ('新約漲價幅度', '比例'), 'marginStep': ('新約貢獻率提升', '文字'),
 'backlogStarted': ('backlog 中已開始交付的比例（法說「>50%」）', '比例'), 'inferenceArr': ('推論服務 ARR（年底）', 'US$bn'), 'otherArr': ('其他服務 ARR', 'US$bn'),
 'convert': ('期後可轉債發行額', 'US$bn'), 'convertNet': ('期後可轉債淨額', 'US$bn'), 'convertCoupon': ('期後可轉債票面利率', '比例'),
 'convertPx': ('轉換價', 'US$'), 'atmShares': ('股權分銷（ATM）上限', 'm 股'), 'price0917': ('9/17 收盤價', 'US$'),
 'tier34Active': ('主動電力位於 Tier 3/4 市場比例', '比例'), 'tier34Contracted': ('簽約電力位於 Tier 3/4 市場比例', '比例'),
 'cdsMid': ('CDS 中價', 'bps'), 'cdsBidAsk': ('CDS 買／賣價', '文字'), 'cdsRange': ('CDS 近期區間', '文字'), 'cdsPeak': ('CDS 峰值', 'bps'),
 'cdsPeakDate': ('CDS 峰值日期', '日期'), 'cdsLow': ('CDS 低點', 'bps'), 'cdsLowDate': ('CDS 低點日期', '日期'),
 'availability': ('未動用信用額度', 'US$bn'), 'price0918': ('9/18 收盤價', 'US$'), 'priceLast': ('最新收盤價', 'US$'),
 'priceDate': ('最新收盤價日期', '日期'), 'q3ShortDated': ('期後公告摘要', '文字'), 'ttmRev': ('近十二個月營收', 'US$bn'),
 'ttmOpInc': ('近十二個月 GAAP 營業損益', 'US$bn'), 'ttmDa': ('近十二個月折舊攤銷', 'US$bn'),
 'ttmOpLease': ('近十二個月營業租賃成本', 'US$bn'), 'mktCapLast': ('CRWV 市值（Comps 用；與同業同一收盤日 peers.priceDate，v4.3 起不隨現價更新）', 'US$bn'), 'nextEarn': ('下次財報時間', '文字'),
}


def get(path):
    v = CO
    for k in path.split('.'): v = v[k]
    return v


def fmt(v):
    if isinstance(v, bool): return '是' if v else '否'
    if isinstance(v, list):
        if v and isinstance(v[0], (dict, list)): return f'{len(v)} 筆'
        return '、'.join(fmt(x) for x in v)
    if isinstance(v, dict): return '物件（' + '、'.join(v) + '）'
    if isinstance(v, str): return v if len(v) <= 28 else v[:26] + '…'
    return f'{v:g}' if isinstance(v, float) else str(v)


# 覆蓋檢查：company.json 每個欄位都要有說明
doc = {p for p, *_ in F} | {f'latestQuarter.{k}' for k in LQ} | {f'callFacts.{k}' for k in CF}
def leaves(o, p=''):
    if isinstance(o, dict):
        for k, v in o.items():
            q = f'{p}.{k}' if p else k
            if q in doc: yield q
            else: yield from leaves(v, q)
    else: yield p
missing = [q for q in leaves(CO) if q not in doc]
assert not missing, f'未說明的欄位：{missing}'
for q in doc: get(q)  # 說明了不存在的欄位會在此報錯

SECT = [('meta', '基本資料'), ('periods', '模型期'), ('actual1H', '上半年實際數（10-Q）'), ('historicalPL', '歷年損益'),
        ('rpo', '已簽約未認列營收（RPO）'), ('leases', '租約'), ('debt', '既有債務'), ('latestQuarter', '最新一季財報數字（10-Q）'),
        ('callFacts', '法說會與期後事項'), ('scenarios', '三個擴張情境'), ('legacy', '舊版對照值'),
        ('defaults', '預設假設（畫面上可調的輸入）'), ('valuation', '評價參數'), ('methodology', '評價方法與評等門檻'), ('peers', '同業比較（Comps）')]
out, shown = [], set()
for top, title in SECT:
    out.append(f'\n### `{top}`：{title}\n')
    if top in ('latestQuarter', 'callFacts'):
        acc = 'LATEST_Q.' if top == 'latestQuarter' else 'CALL_FACTS.'
        tbl = LQ if top == 'latestQuarter' else CF
        out.append('換公司：全部必改（公司特有資料）。「程式使用」為否的欄位只是存檔備查，畫面與 Excel 的說明文字目前另外寫在程式裡。\n')
        out.append('| 欄位 | 意義 | 單位 | 目前數值 | 程式使用 |\n|---|---|---|---|---|')
        for k, (m, u) in tbl.items():
            used = re.search(rf"({re.escape(acc)}|{top}'\]\['){k}\b", CODE) is not None
            out.append(f'| `{k}` | {m} | {u} | {fmt(CO[top][k])} | {"是" if used else "否"} |')
        continue
    out.append('| 欄位 | 意義 | 單位 | 目前數值 | 換公司 |\n|---|---|---|---|---|')
    for p, m, u, c in F:
        if p == top or p.startswith(top + '.') or (top == 'periods' and p == 'periodYears'):
            shown.add(p)
            out.append(f'| `{p}` | {m} | {u} | {fmt(get(p))} | {c} |')
assert shown == {p for p, *_ in F}, set(p for p, *_ in F) - shown
print('\n'.join(out))
