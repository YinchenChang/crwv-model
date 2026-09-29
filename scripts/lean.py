# 精簡版（PR #12；已決定事項 13）：由建好的完整版 Excel 刪減出精簡版 Excel——不另寫模型公式，數字與完整版相同。
# 做法：scripts/lean_deps.py 算出精簡版目標的依賴鏈（以「分頁＋A 欄列名稱」定義目標，整列保留的不動點），
#   以 LibreOffice（UNO）刪除依賴鏈外的分頁與列（LibreOffice 刪列時自動改寫所有參照），並清除 I 欄起不被任何公式引用的說明文字（移除清單 B13）。
#   另寫出精簡版的 outline 對照（舊列號 → 新列號）供 fix_outline.py 使用。
# 之後的處理與完整版相同：recalc → fix_outline（本檔寫出的 outline）→ fix_datatable → verify_ooxml；再以 scripts/lean_check.py 與完整版逐項比較。
# 用法：python3 scripts/lean.py 完整版.xlsx 精簡版.xlsx [完整版 outline.json，預設 out/outline.json] [精簡版 outline 輸出，預設 out/outline_lean.json]
import sys, os, json, shutil
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from uno_q import Workbook
from lean_deps import analyse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
full, lean = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
ol_in = sys.argv[3] if len(sys.argv) > 3 else os.path.join(ROOT, 'out', 'outline.json')
ol_out = sys.argv[4] if len(sys.argv) > 4 else os.path.join(ROOT, 'out', 'outline_lean.json')
NOTE_COL = 9  # I 欄起為說明欄（build_xlsx.py 慣例）

A = analyse(full)
wbx, keep_cells = A['wb'], A['keep']
keep = {}
for (s, r) in A['rows']:
    keep.setdefault(s, set()).add(r)
for s in keep:   # 標題、表頭與各區段標題
    ws = wbx[s]
    keep[s] |= {1, 2, 3, 4}
    for r in range(1, ws.max_row + 1):
        a = ws.cell(r, 1).value
        if isinstance(a, str) and ws.cell(r, 1).fill is not None and ws.cell(r, 1).fill.fgColor is not None and ws.cell(r, 1).fill.fgColor.rgb == 'FFD9E2F3':
            keep[s].add(r)
drop_sheets = [s for s in wbx.sheetnames if s not in keep]
rowmap = {s: {r: i + 1 for i, r in enumerate(sorted(keep[s]))} for s in keep}
# 說明欄：I 欄起、純文字（非公式）、不在依賴鏈內的格
notes = {s: [(r, c) for r in keep[s] for c in range(NOTE_COL, wbx[s].max_column + 1)
             if isinstance(wbx[s].cell(r, c).value, str) and not wbx[s].cell(r, c).value.startswith('=') and (s, r, c) not in keep_cells]
         for s in keep}

shutil.copy(full, lean)
with Workbook(lean, timeout=90) as wb:
    doc = wb.doc
    for s in drop_sheets: doc.Sheets.removeByName(s)
    for s, rows in keep.items():
        sh = doc.Sheets.getByName(s)
        for r, c in notes[s]: sh.getCellByPosition(c - 1, r - 1).setString('')
        cur = sh.createCursor(); cur.gotoEndOfUsedArea(False); last = cur.RangeAddress.EndRow + 1
        blocks = []
        for r in sorted((r for r in range(1, last + 1) if r not in rows), reverse=True):  # 由下往上、連續區塊一次刪
            if blocks and blocks[-1][0] == r + 1: blocks[-1][0] = r
            else: blocks.append([r, r])
        for a, b in blocks: sh.Rows.removeByIndex(a - 1, b - a + 1)
    from com.sun.star.beans import PropertyValue
    pv = PropertyValue(); pv.Name = 'FilterName'; pv.Value = 'Calc MS Excel 2007 XML'
    doc.storeToURL(Path(lean).as_uri(), (pv,))

ol = json.load(open(ol_in, encoding='utf-8'))
json.dump({s: [[rowmap[s][hr], lv, col] for hr, lv, col in v if hr in rowmap[s]] for s, v in ol.items() if s in rowmap},
          open(ol_out, 'w', encoding='utf-8'), ensure_ascii=False)
F = sum(1 for k in A['keep'] if A['kind'].get(k) == 'f')
print(f"精簡版：刪除分頁 {len(drop_sheets)} 張（{'、'.join(drop_sheets)}）；保留 {len(keep)} 張、{sum(len(v) for v in keep.values())} 列、公式 {F} 個；"
      f"清除說明 {sum(len(v) for v in notes.values())} 格 → {lean}")
