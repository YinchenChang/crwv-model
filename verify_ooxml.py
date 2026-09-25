# Excel 嚴格檢查項目的離線核對（LibreOffice／openpyxl 不檢查、Excel 會拒絕開啟的問題）。
# 用法：python3 verify_ooxml.py 檔案.xlsx   → 全部通過時輸出 OOXML OK，否則列出問題並以代碼 1 結束。
import sys, zipfile, re
from xml.dom import minidom
SEQ = ['sheetPr','dimension','sheetViews','sheetFormatPr','cols','sheetData','sheetCalcPr','sheetProtection',
       'protectedRanges','scenarios','autoFilter','sortState','dataConsolidate','customSheetViews','mergeCells',
       'phoneticPr','conditionalFormatting','dataValidations','hyperlinks','printOptions','pageMargins','pageSetup',
       'headerFooter','rowBreaks','colBreaks','customProperties','cellWatches','ignoredErrors','smartTags','drawing',
       'legacyDrawing','legacyDrawingHF','picture','oleObjects','controls','webPublishItems','tableParts','extLst']
SP = ['tabColor', 'outlinePr', 'pageSetUpPr']
z = zipfile.ZipFile(sys.argv[1]); err = []
if z.testzip(): err.append('ZIP CRC 錯誤')
for n in z.namelist():
    d = z.read(n)
    if n.endswith(('.xml', '.rels')):
        try: minidom.parseString(d)
        except Exception as e: err.append(f'{n}: XML 格式錯誤 {e}')
    if not n.startswith('xl/worksheets/sheet'): continue
    s = d.decode()
    body = re.search(r'<worksheet[^>]*>(.*)</worksheet>', s, re.S).group(1)
    top, depth = [], 0
    for m in re.finditer(r'<(/?)(\w+)[^>]*?(/?)>', body):
        c, t, sc = m.groups()
        if c: depth -= 1; continue
        if depth == 0: top.append(t)
        if not sc: depth += 1
    idx = [SEQ.index(t) if t in SEQ else -1 for t in top]
    if -1 in idx or idx != sorted(idx): err.append(f'{n}: 工作表子元素順序錯誤 {top}')
    sp = re.search(r'<sheetPr[^>]*>(.*?)</sheetPr>', s, re.S)
    kids = re.findall(r'<(\w+)', sp.group(1)) if sp else []
    if kids != [k for k in SP if k in kids]: err.append(f'{n}: sheetPr 子元素順序錯誤 {kids}')
print('\n'.join(err) if err else 'OOXML OK'); sys.exit(1 if err else 0)
