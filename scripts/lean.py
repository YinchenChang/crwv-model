# 精簡版（PR #12；已決定事項 13）：由建好的完整版 Excel 刪減出精簡版 Excel——不另寫模型公式，數字與完整版相同。
# 做法：scripts/lean_deps.py 算出精簡版目標的依賴鏈（以「分頁＋A 欄列名稱」定義目標，整列保留的不動點），
#   以 LibreOffice（UNO）刪除依賴鏈外的分頁與列（LibreOffice 刪列時自動改寫所有參照），並清除 I 欄起不被任何公式引用的說明文字（移除清單 B13）。
#   再依 MERGES 把小分頁整塊併入目的分頁的底部或頂部、依 RENAMES 改名（LibreOffice 搬移、插列、改名時自動改寫引用）。
#   另寫出精簡版的 outline 對照（舊列號 → 新列號）供 fix_outline.py 使用，以及合併對照（*_merges.json）供 lean_check.py 找格。
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
# (來源, 目的, 位置)：來源整塊併到目的分頁的底部（bottom）或頂部（top）；依序執行。第一批（第 6 輪）3 組、第二批（第 7 輪）2 組，皆經 Andy 逐組核可。
#   各期收支底部依序為：既有債務 → 新債與新股（既有債務 → 新債 → 新股 → 淨負債連續呈現，Andy 指定）。
MERGES = [('評價_反向DCF', '評價_DCF與目標價', 'bottom'), ('檢查_連動', '摘要', 'bottom'),
          ('資產負債_既有債務', '各期收支', 'bottom'), ('資產負債_新債與新股', '各期收支', 'bottom'),
          ('損益', '評價_DCF與目標價', 'top')]
RENAMES = {'評價_DCF與目標價': '損益與評價'}  # 合併後改名（只改精簡版；第 7 輪 Andy 核可）

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
    # 分頁合併（第 6 輪，Andy 核可第一批 3 組；已決定事項 9 逐組核可）：來源分頁整塊搬到目的分頁底部（空一列），
    # LibreOffice 搬移儲存格時自動改寫所有引用（與剪下貼上相同），再刪除空的來源分頁。
    from com.sun.star.table import CellAddress
    pos = {s: (s, 0) for s in keep}   # 各原分頁的列在精簡版的位置：(最後所在分頁, 列號位移)
    for src, dst, where in MERGES:
        if not (doc.Sheets.hasByName(src) and doc.Sheets.hasByName(dst)): continue
        ssh, dsh = doc.Sheets.getByName(src), doc.Sheets.getByName(dst)
        c1 = ssh.createCursor(); c1.gotoEndOfUsedArea(False); ra = c1.RangeAddress
        src_rng = ssh.getCellRangeByPosition(0, 0, ra.EndColumn, ra.EndRow).RangeAddress
        n = ra.EndRow + 1
        if where == 'top':   # 目的分頁頂部先插入 n＋1 列（空一列分隔；插入時 LibreOffice 同樣改寫引用）
            dsh.Rows.insertByIndex(0, n + 1); start = 0
            pos = {s: (d, o + n + 1 if d == dst else o) for s, (d, o) in pos.items()}
        else:
            c2 = dsh.createCursor(); c2.gotoEndOfUsedArea(False); start = c2.RangeAddress.EndRow + 2   # 0 起算：空一列
        dest = CellAddress(); dest.Sheet = dsh.RangeAddress.Sheet; dest.Column = 0; dest.Row = start
        dsh.moveRange(dest, src_rng)
        doc.Sheets.removeByName(src)
        pos = {s: ((dst, start + o) if d == src else (d, o)) for s, (d, o) in pos.items()}
    for old, new in RENAMES.items():
        if doc.Sheets.hasByName(old): doc.Sheets.getByName(old).setName(new)
    pos = {s: (RENAMES.get(d, d), o) for s, (d, o) in pos.items()}
    moved = {s: d for s, (d, o) in pos.items() if d != s}
    from com.sun.star.beans import PropertyValue
    pv = PropertyValue(); pv.Name = 'FilterName'; pv.Value = 'Calc MS Excel 2007 XML'
    doc.storeToURL(Path(lean).as_uri(), (pv,))

ol = json.load(open(ol_in, encoding='utf-8'))
lean_ol = {}
for s, v in ol.items():
    if s not in rowmap: continue
    dst, off = pos[s]
    lean_ol.setdefault(dst, []).extend([rowmap[s][hr] + off, lv, col] for hr, lv, col in v if hr in rowmap[s])
json.dump(lean_ol, open(ol_out, 'w', encoding='utf-8'), ensure_ascii=False)
json.dump(moved, open(os.path.splitext(ol_out)[0] + '_merges.json', 'w', encoding='utf-8'), ensure_ascii=False)
F = sum(1 for k in A['keep'] if A['kind'].get(k) == 'f')
print(f"精簡版：刪除分頁 {len(drop_sheets)} 張（{'、'.join(drop_sheets)}）；合併與改名 {len(moved)} 項（{'、'.join(f'{a}→{b}' for a, b in moved.items())}）；"
      f"最後 {len(set(d for d, _ in pos.values()))} 張、{sum(len(v) for v in keep.values())} 列、公式 {F} 個；"
      f"清除說明 {sum(len(v) for v in notes.values())} 格 → {lean}")
