# 精簡版 第 3 輪：可行性測試（不入建置流程；結果寫在 docs/reports/20260928_精簡版.md）
# 問題：以 LibreOffice（UNO）刪除完整版 Excel 中「不在精簡版目標依賴鏈內」的列與分頁後，
#   (1) 公式參照是否自動改寫、重算 0 錯誤；(2) 模擬運算表經 fix_datatable 還原、verify_ooxml 通過；(3) outline 可依列號對照表補回；
#   (4) 三情境 × 兩種 DCF 模式的目標價、評等與資金缺口等與完整版逐項一致。
# 用法：python3 docs/reports/20260928_精簡版_可行性測試.py 完整版.xlsx（verify.sh 建好的 out/ 檔） 輸出目錄
import sys, os, json, time, shutil, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from uno_q import Workbook

full, outdir = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
outdir.mkdir(parents=True, exist_ok=True)
lean = outdir / 'lean.xlsx'
shutil.copy(full, lean)

# ── 1. 依賴鏈（沿用第 2 輪的目標定義）：保留的 (分頁, 列)
from lean_deps import analyse   # 第 4 輪起依賴分析移到 scripts/lean_deps.py
A = analyse(str(full)); allk, kind, wbx = A['allk'], A['kind'], A['wb']
keep = {}
for (s, r) in A['rows']:   # 列層級不動點（含被引用但目前空白的輸入格）
    keep.setdefault(s, set()).add(r)
# 各分頁保留標題與表頭（第 1–4 列）；摘要保留各區段標題（A 欄以「數字｜」開頭）
for s in keep:
    keep[s] |= {1, 2, 3, 4}
    ws = wbx[s]
    for r in range(1, ws.max_row + 1):
        a = ws.cell(r, 1).value
        if isinstance(a, str) and len(a) > 1 and a[0].isdigit() and a[1] == '｜': keep[s].add(r)
drop_sheets = [s for s in wbx.sheetnames if s not in keep]
rowmap = {s: {r: i + 1 for i, r in enumerate(sorted(keep[s]))} for s in keep}

# ── 2. UNO 刪列、刪分頁、存檔
t0 = time.time()
with Workbook(str(lean), timeout=90) as wb:
    doc = wb.doc
    for s in drop_sheets: doc.Sheets.removeByName(s)
    for s, rows in keep.items():
        sh = doc.Sheets.getByName(s)
        cur = sh.createCursor(); cur.gotoEndOfUsedArea(False); last = cur.RangeAddress.EndRow + 1
        dels = [r for r in range(1, last + 1) if r not in rows]
        # 由下往上、連續區塊一次刪除
        blocks = []
        for r in sorted(dels, reverse=True):
            if blocks and blocks[-1][0] == r + 1: blocks[-1][0] = r
            else: blocks.append([r, r])
        for a, b in blocks: sh.Rows.removeByIndex(a - 1, b - a + 1)
    from com.sun.star.beans import PropertyValue
    pv = PropertyValue(); pv.Name = 'FilterName'; pv.Value = 'Calc MS Excel 2007 XML'
    doc.storeToURL(lean.as_uri(), (pv,))
t_prune = time.time() - t0

# ── 3. 建置後處理：重算 → outline（列號對照）→ 模擬運算表 → OOXML
ol = json.load(open(ROOT / 'out/outline.json', encoding='utf-8'))
lean_ol = {s: [[rowmap[s][hr], lv, col] for hr, lv, col in v if hr in rowmap.get(s, {})] for s, v in ol.items() if s in rowmap}
json.dump(lean_ol, open(outdir / 'outline_lean.json', 'w', encoding='utf-8'), ensure_ascii=False)
steps = {}
def run(name, cmd):
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    steps[name] = (p.returncode, (p.stdout + p.stderr).strip().splitlines()[-1:] or [''])
    return p.returncode == 0
run('recalc', ['python3', 'scripts/recalc.py', str(lean), '180'])
run('fix_outline', ['python3', 'fix_outline.py', str(lean), str(outdir / 'outline_lean.json')])
run('fix_datatable', ['python3', 'fix_datatable.py', str(lean)])
run('verify_ooxml', ['python3', 'verify_ooxml.py', str(lean)])

# ── 4. 與完整版逐項比較（依 分頁＋A 欄列名稱 找格，兩邊都用 UNO 改情境與 DCF 模式後讀值）
IN, VA, CF = '輸入與假設', '評價_DCF與目標價', '各期收支'
PROBES = [(VA, '加權目標價', 'C'), (VA, '目標價區間｜點位評等代碼（1＝買進、0＝中立、−1＝賣出）', 'C'),
          (VA, '目標價區間｜情境區間（下緣／上緣）', 'C'), (VA, '目標價區間｜情境區間（下緣／上緣）', 'D'),
          (VA, '目標價區間｜方法區間（下緣／上緣）', 'C'), (VA, '目標價區間｜方法區間（下緣／上緣）', 'D'),
          (VA, '目標價區間｜賣出門檻價（現價 × (1 − 15%)）', 'C'), (VA, 'DCF 每股', 'C'), (VA, 'EV/EBITDA 每股（融資後）', 'C'),
          ('摘要', '差異｜判斷句', 'C'), ('摘要', '結論｜結論句', 'C'), ('摘要', '差異｜差異原因摘要', 'C')] + \
         [(CF, lab, col) for lab in ('營運缺口（不含融資、不含還本）', '股權募資', '新發行股數', '累計新股', '期末總債務（既有＋可轉債＋新債＋高息債）', '新債舉借', '高息債舉借（溢出）')
          for col in 'CDEFG'] + \
         [('季度追蹤', lab, col) for lab in ('焦點｜營收', '焦點｜調整後營業利益', '焦點｜CapEx（毛額）') for col in 'CDEF']

def read(path):
    out, dt = {}, None
    with Workbook(str(path), timeout=90) as wb:
        sc, md = wb.cell(IN, '情境選擇（', prefix=True), wb.cell(IN, 'DCF 下限方式（', prefix=True)
        refs = {p: wb.cell(p[0], p[1], col=p[2]) for p in PROBES}
        t1 = time.time(); n = 0
        for s in (1, 2, 3):
            for m in (1, 2):
                wb.set(sc, s); wb.set(md, m); n += 1
                for p, (sh, a) in refs.items():
                    c = sh.getCellRangeByName(a)
                    out[(s, m) + p] = (c.getValue(), c.getString())  # 數值與顯示字串都比
        dt = (time.time() - t1) / n
    return out, dt
F, t_full = read(full)
L, t_lean = read(lean)
diff = [(k, F[k], L[k]) for k in F if not (F[k][1] == L[k][1] and abs(F[k][0] - L[k][0]) < 1e-9)]

# ── 5. 規模
import openpyxl
from openpyxl.worksheet.formula import DataTableFormula
def size(p):
    w = openpyxl.load_workbook(p); f = n = ch = rows = 0
    for ws in w.worksheets:
        rows += ws.max_row
        for row in ws.iter_rows():
            for x in row:
                v = x.value
                if isinstance(v, DataTableFormula) or (isinstance(v, str) and v.startswith('=')): f += 1
                elif isinstance(v, str): ch += len(v)
                elif isinstance(v, (int, float)): n += 1
    return len(w.worksheets), f, n, rows, ch
res = {'刪除分頁': drop_sheets, '刪列＋存檔秒數': round(t_prune, 1), '後處理': steps,
       '比較項數': len(F), '差異': [(list(k), a, b) for k, a, b in diff][:20], '差異數': len(diff),
       '每次重算讀值秒數（完整／精簡）': [round(t_full, 2), round(t_lean, 2)],
       '規模（分頁、公式、數值、列、文字字數）': {'完整版': size(full), '精簡版': size(lean)}}
print(json.dumps(res, ensure_ascii=False, indent=1))
json.dump(res, open(outdir / 'result.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
sys.exit(0 if not diff and all(v[0] == 0 for v in steps.values()) else 1)
