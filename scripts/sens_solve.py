# 精簡版（PR #12）：翻轉倍數、現價隱含倍數、翻轉 WACC、關鍵假設 ±10%——建置時由 Python 重跑 Excel 求得（已決定事項 8、13）。
# 以 LibreOffice（UNO）開啟建好的 Excel，逐情境（0 截斷口徑）改輸入、重算、讀值；結果寫入 sens_snap.json，
# build_xlsx.py 讀此檔寫入「評價_DCF與目標價」底部「穩健性與關鍵假設」段（完整版與精簡版共用）。
#   翻轉倍數＝評等離開「賣出」所需的最小 EV/EBITDA 倍數（由目前倍數往上掃描；已非賣出時不算）。
#   現價隱含倍數＝EV/EBITDA 腿（模型錨定年、折回目標價時點）等於現價的倍數（對半求解）。
#   翻轉 WACC＝評等離開「賣出」所需的最高 WACC（由目前 WACC 往下掃描）。
#   關鍵假設＝company.json → methodology.keyAssumptions 的候選各上下一步（rel＝相對 ±step、abs＝絕對 ±step；逐年列整列同改），
#     依目標價變動絕對值（兩端取大）排序，取前 topN 名。
# 用法：python3 scripts/sens_solve.py 檔案.xlsx [輸出 json，預設 repo 根目錄 sens_snap.json]
#   結果與原檔相同時代碼 0；有變動時寫入並以代碼 3 結束（verify.sh 據此重建 Excel，與 rv_solve.py 相同）。
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from uno_q import Workbook

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
xlsx = sys.argv[1]; out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, 'sens_snap.json')
CO = json.load(open(os.path.join(ROOT, 'company.json'), encoding='utf-8'))
KA, FS = CO['methodology']['keyAssumptions'], CO['methodology']['flipSearch']
IN, VA = '輸入與假設', '評價_DCF與目標價'
COLS = 'CDEFG'
SELL = -1


def unique_row(wb, sheet, prefix):
    """A 欄以 prefix 開頭、且 C 欄有數值的列必須剛好一列（候選清單寫錯或列名稱重複即報錯，不猜）。"""
    sh = wb.doc.Sheets.getByName(sheet)
    cur = sh.createCursor(); cur.gotoEndOfUsedArea(False); last = cur.RangeAddress.EndRow + 1
    hits = [r for r in range(1, last + 1) if sh.getCellRangeByName(f'A{r}').getString().startswith(prefix)
            and sh.getCellRangeByName(f'C{r}').getFormula() != '' and not sh.getCellRangeByName(f'C{r}').getFormula().startswith('=')]
    if len(hits) != 1: raise KeyError(f'{sheet}｜「{prefix}」開頭的輸入列應剛好一列，找到 {hits}')
    return sh, hits[0]


r6 = lambda x: None if x is None else round(x, 6)
res = {'note': KA['note'], 'topN': KA['topN'], 'scenarios': []}
with Workbook(xlsx, timeout=90) as wb:
    sc = wb.cell(IN, '情境選擇（', prefix=True); md = wb.cell(IN, 'DCF 下限方式（', prefix=True)
    tgt, leg = wb.cell(VA, '加權目標價'), wb.cell(VA, 'EV/EBITDA 每股（融資後）')
    rate = wb.cell(VA, '目標價區間｜點位評等代碼（', prefix=True)
    mult, wacc, px = wb.cell(IN, 'EV/EBITDA 倍數'), wb.cell(IN, 'WACC'), wb.cell(IN, '現價（', prefix=True)
    cand = []
    for c in KA['candidates']:
        sh, r = unique_row(wb, IN, c['label'])
        cells = [(sh, f'{col}{r}') for col in (COLS if c['perYear'] else 'C')]
        cand.append((c, cells))
    sc0, md0 = wb.get(sc), wb.get(md)
    wb.set(md, 1)  # 0 截斷口徑（評等依據）
    P = wb.get(px)
    for s in (1, 2, 3):
        wb.set(sc, s)
        base, code = wb.get(tgt), wb.get(rate)
        row = {'scenario': s, 'target': r6(base), 'rating': code}
        # 翻轉倍數
        m0 = wb.get(mult); flip = None
        if code == SELL:
            k = 1
            while m0 + k * FS['multipleStep'] <= FS['multipleMax'] + 1e-9:
                wb.set(mult, m0 + k * FS['multipleStep'])
                if wb.get(rate) != SELL: flip = m0 + k * FS['multipleStep']; break
                k += 1
        # 現價隱含倍數（EV/EBITDA 腿＝現價；腿對倍數遞增）
        lo, hi = 0.0, FS['multipleMax'] * 2; wb.set(mult, hi); implied = None
        if wb.get(leg) >= P:
            for _ in range(40):
                mid = (lo + hi) / 2; wb.set(mult, mid)
                if wb.get(leg) >= P: hi = mid
                else: lo = mid
            implied = (lo + hi) / 2
        wb.set(mult, m0)
        row['flipMultiple'], row['impliedMultiple'] = r6(flip), r6(implied)
        # 翻轉 WACC
        w0 = wb.get(wacc); fw = None
        if code == SELL:
            k = 1
            while w0 - k * FS['waccStep'] >= FS['waccMin'] - 1e-9:
                wb.set(wacc, w0 - k * FS['waccStep'])
                if wb.get(rate) != SELL: fw = w0 - k * FS['waccStep']; break
                k += 1
        wb.set(wacc, w0)
        row['flipWacc'] = r6(fw)
        # 關鍵假設
        ka = []
        for c, cells in cand:
            v0 = [wb.get(x) for x in cells]; d = []
            for sgn in (-1, 1):
                for x, v in zip(cells, v0):
                    wb.set(x, v * (1 + sgn * c['step']) if c['mode'] == 'rel' else v + sgn * c['step'])
                d.append(wb.get(tgt) - base)
            for x, v in zip(cells, v0): wb.set(x, v)
            ka.append({'name': c['name'], 'down': r6(d[0]), 'up': r6(d[1]), 'mode': c['mode'], 'step': c['step']})
        ka.sort(key=lambda e: -max(abs(e['down']), abs(e['up'])))
        row['keyAssumptions'] = ka
        if abs(wb.get(tgt) - base) > 1e-9: raise RuntimeError('輸入還原後目標價不同：求解過程改動了輸入')
        res['scenarios'].append(row)
    wb.set(sc, sc0); wb.set(md, md0)

txt = json.dumps(res, ensure_ascii=False, indent=1)
for row in res['scenarios']:
    top = '、'.join(f"{e['name']} {e['down']:+.1f}／{e['up']:+.1f}" for e in row['keyAssumptions'][:res['topN']])
    print(f"情境 {row['scenario']}：目標價 {row['target']:.2f}、翻轉倍數 {row['flipMultiple']}、現價隱含倍數 {row['impliedMultiple']}、翻轉 WACC {row['flipWacc']}；前三：{top}")
old = open(out, encoding='utf-8').read() if os.path.exists(out) else None
if old == txt:
    print('sens_snap.json 無變動'); sys.exit(0)
open(out, 'w', encoding='utf-8').write(txt)
print(f'sens_snap.json 已更新（{out}）'); sys.exit(3)
