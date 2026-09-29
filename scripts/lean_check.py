# 精簡版（PR #12）驗收：精簡版與完整版在「三情境 × 兩種 DCF 模式」下逐項一致（已決定事項 13）。
# 兩邊都以 LibreOffice（UNO）開啟，改情境選擇與 DCF 下限方式後讀值；以「分頁＋A 欄列名稱」找格，數值差 < 1e-9 且顯示字串相同才算一致。
# 比較項：目標價與評等（含情境區間、方法區間、賣出門檻、兩條腿）、資金缺口與融資（5 期）、FY28 起未簽約收入占比、焦點季、
#   結論句與判斷句、差異原因摘要、穩健性與關鍵假設（快照與句子）。
# 用法：python3 scripts/lean_check.py 完整版.xlsx 精簡版.xlsx
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from uno_q import Workbook

IN, VA, CF, SM, QT = '輸入與假設', '評價_DCF與目標價', '各期收支', '摘要', '季度追蹤'
P = [(VA, '加權目標價', 'C'), (VA, '目標價區間｜點位評等代碼（', 'C'), (VA, '目標價區間｜點位評等代碼（', 'D'),
     (VA, '目標價區間｜情境區間（下緣／上緣）', 'C'), (VA, '目標價區間｜情境區間（下緣／上緣）', 'D'),
     (VA, '目標價區間｜方法區間（下緣／上緣）', 'C'), (VA, '目標價區間｜方法區間（下緣／上緣）', 'D'),
     (VA, '目標價區間｜賣出門檻價（', 'C'), (VA, 'DCF 每股', 'C'), (VA, 'EV/EBITDA 每股（融資後）', 'C'),
     (VA, '目標價區間｜判斷句', 'C'), (VA, '穩健性｜翻轉倍數句', 'C'), (VA, '對照｜共識倍數句', 'C'), (VA, '對照｜同式：共識平均目標價以模型數字換算的 EV/EBITDA（目前情境，活公式）', 'C'), (VA, '穩健性｜翻轉 WACC 句', 'C'),
     (VA, '關鍵假設｜句（目前情境）', 'C'), (VA, '快照｜狀態', 'C'),
     (SM, '結論｜結論句', 'C'), (SM, '差異｜判斷句', 'C'), (SM, '差異｜差異原因摘要', 'C'), (SM, '隱含｜隱含倍數句', 'C'),
     ('檢查_連動', 'FY28 起收入是否依賴未簽約', 'B')] + \
    [(CF, lab, col) for lab in ('營運缺口（不含融資、不含還本）', '期末累積現金', '新債舉借', '股權募資', '高息債舉借（溢出）', '新發行股數',
                                '累計新股', '期末總債務（既有＋可轉債＋新債＋高息債）') for col in 'CDEFG'] + \
    [(QT, lab, col) for lab in ('焦點｜營收', '焦點｜調整後 EBITDA', '焦點｜調整後營業利益', '焦點｜CapEx（毛額）', '焦點｜差異原因') for col in 'CDEFGHI']


def read(path):
    out = {}
    with Workbook(path, timeout=90) as wb:
        sc, md = wb.cell(IN, '情境選擇（', prefix=True), wb.cell(IN, 'DCF 下限方式（', prefix=True)
        refs = {p: wb.cell(p[0], p[1], col=p[2], prefix=p[1].endswith('（'), need_value=False) for p in P}
        for s in (1, 2, 3):
            for m in (1, 2):
                wb.set(sc, s); wb.set(md, m)
                for p, (sh, a) in refs.items():
                    c = sh.getCellRangeByName(a); out[(s, m) + p] = (c.getValue(), c.getString(), c.getError())
    return out


F, L = read(sys.argv[1]), read(sys.argv[2])
bad = [(k, F[k], L.get(k)) for k in F if L.get(k) is None or F[k][2] or L[k][2] or F[k][1] != L[k][1] or abs(F[k][0] - L[k][0]) >= 1e-9]
print(f'精簡版 vs 完整版：三情境 × 兩種 DCF 模式，共 {len(F)} 項；不一致 {len(bad)} 項')
for k, a, b in bad[:15]: print('  ', k, a, b)
sys.exit(1 if bad or not F else 0)
