# Excel 逐格比對（公式與常數；另可比對重算後的值）。用法：python3 xl_diff.py a.xlsx b.xlsx [--values]
import sys, re, openpyxl
a, b = sys.argv[1], sys.argv[2]; vals = '--values' in sys.argv
norm = lambda v: re.sub(r'v\d\.\d', 'vX', v) if isinstance(v, str) else v
wa, wb = openpyxl.load_workbook(a, data_only=vals), openpyxl.load_workbook(b, data_only=vals)
diffs = []
if wa.sheetnames != wb.sheetnames: diffs.append(('sheets', wa.sheetnames, wb.sheetnames))
for n in wa.sheetnames:
    if n not in wb.sheetnames: continue
    A, B = wa[n], wb[n]
    for r in range(1, max(A.max_row, B.max_row) + 1):
        for c in range(1, max(A.max_column, B.max_column) + 1):
            x, y = norm(A.cell(r, c).value), norm(B.cell(r, c).value)
            if x != y and not (isinstance(x, float) and isinstance(y, float) and abs(x - y) < 1e-9):
                diffs.append((n, A.cell(r, c).coordinate, str(x)[:70], str(y)[:70]))
print(len(diffs), 'differences'); [print(*d) for d in diffs[:15]]
