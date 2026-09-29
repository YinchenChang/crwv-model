# 精簡版 第 3 輪：Andy 補充 (1)(2) 的試算（不入建置流程；實作時改為建置步驟並寫入 Excel）
#   (1) 各情境「翻轉評等所需的 EV/EBITDA 倍數」：評等代碼離開「賣出」的最小倍數（0 截斷口徑）。
#   (2) 關鍵假設：候選輸入各 ±10%（相對值；逐年列整列同乘），重跑 Excel，依目標價變動絕對值排序；
#       「保守情境翻轉為非賣出所需的 WACC」。
# 用法：python3 docs/reports/20260928_精簡版_敏感度試算.py 完整版.xlsx
import sys, json, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from uno_q import Workbook

IN, VA = '輸入與假設', '評價_DCF與目標價'
# 候選：(名稱, A 欄列名稱, 是否逐年列)；列名稱以開頭比對
CAND = [('每 MW 年收入', '每 MW 年收入倍數（整體）', False), ('每 MW 建置成本', '每 MW 建置成本倍數（整體）', False),
        ('穩態 EBITDA 率', '穩態 EBITDA 率（FY30）', False), ('WACC', 'WACC', False), ('永續成長 g', '永續成長 g', False),
        ('EV/EBITDA 倍數', 'EV/EBITDA 倍數', False), ('利用率', '利用率', True), ('新產能簽約率', '新產能簽約率', True),
        ('債務／backlog 上限', '債務／backlog 上限', False), ('新債利率', '新債利率', True), ('終值維持性 CapEx', '終值維持性 CapEx 占 D&A', False),
        ('股權發行折價', '股權發行折價', False), ('客戶違約率', '客戶違約率', True), ('起始 EBITDA 率', '起始 EBITDA 率（FY26）', False)]
COLS = 'CDEFG'

out = {}
t0 = time.time(); n = 0
with Workbook(sys.argv[1], timeout=90) as wb:
    sc, md = wb.cell(IN, '情境選擇（', prefix=True), wb.cell(IN, 'DCF 下限方式（', prefix=True)
    tgt, rate, sell = wb.cell(VA, '加權目標價'), wb.cell(VA, '目標價區間｜點位評等代碼（1＝買進、0＝中立、−1＝賣出）'), wb.cell(VA, '目標價區間｜賣出門檻價（', prefix=True)
    mult, wacc = wb.cell(IN, 'EV/EBITDA 倍數'), wb.cell(IN, 'WACC')
    refs = {}
    for name, lab, per in CAND:
        sh, a = wb.cell(IN, lab)
        r = a[1:]
        refs[name] = [(sh, f'{c}{r}') for c in (COLS if per else 'C')]
    wb.set(md, 1)
    for s in (1, 2, 3):
        wb.set(sc, s); base = wb.get(tgt); n += 1
        row = {'基準目標價': round(base, 2), '評等代碼': wb.get(rate), '賣出門檻價': round(wb.get(sell), 2), '±10%': {}}
        for name, cells in refs.items():
            v0 = [wb.get(c) for c in cells]; res = []
            for f in (0.9, 1.1):
                for c, v in zip(cells, v0): wb.set(c, v * f)
                res.append(wb.get(tgt) - base); n += 1
            for c, v in zip(cells, v0): wb.set(c, v)
            row['±10%'][name] = [round(res[0], 2), round(res[1], 2)]
        # (1) 翻轉評等所需倍數：由 6x 往上掃描，評等代碼 ≠ −1 的第一個倍數（0.05x 精度）；10x 內無解記 None
        m0 = wb.get(mult); flip = None; x = m0
        while x <= 10.0001:
            wb.set(mult, x); n += 1
            if wb.get(rate) != -1: flip = round(x, 2); break
            x += 0.05
        wb.set(mult, m0)
        row['翻轉倍數'] = flip
        # (2) 翻轉為非賣出所需的 WACC：由目前 WACC 往下掃描（0.05pt 精度），6% 內無解記 None
        w0 = wb.get(wacc); fw = None; x = w0
        while x >= 0.06 - 1e-9:
            wb.set(wacc, x); n += 1
            if wb.get(rate) != -1: fw = round(x, 4); break
            x -= 0.0005
        wb.set(wacc, w0)
        row['翻轉 WACC'] = fw
        out[s] = row
out['重算次數'] = n; out['秒數'] = round(time.time() - t0, 1)
print(json.dumps(out, ensure_ascii=False, indent=1))
