# v4.5（5a-1）：期間滾動——由 company.json → calendar 推算模型期間、日期與折現年數（Excel 與 HTML 共用同一份推算結果）。
# 輸入（company.json → calendar）：
#   fiscalYearEndMonth    財年結束月份（CoreWeave 12；Oracle 5）
#   latestQuarterFiled    最新已申報（10-Q／10-K）的財季，例如 "FY26Q2"；驅動年度首期。null＝沒有已申報季度（例如未上市公司）
#   latestQuarterReported 最新已公布（財報新聞稿）的財季；驅動季度層（年度首期不受影響）
#   modelYears            首期之後的完整財年數（固定期數滾動；Andy 2026-09-26 決定 4）
#   targetHorizon         目標價時點：firstFullYearEnd＝首期之後第一個完整財年末；valuationPlus12m＝評價日＋12 個月
#   firstModelFY          latestQuarterFiled 為 null 時的首個模型財年，例如 "FY26"（首期＝全年模型）
# 推算（全部以「月」計算，期末都是月底，所以 6 個月＝0.5 年，無天數誤差）：
#   評價日＝已申報季度的季末（沒有時＝首個模型財年的前一財年末）；首期＝該財年剩餘季度的模型部分（0.25／0.5／0.75／1 年）；
#   Q4 已申報時首期為下一財年的全年模型。期間標籤 FYyy 的 yy＝財年結束所在的日曆年。
# 用法：python3 calendar_q.py [repo 目錄] → 印出推算結果（JSON；load_engine.js 以此注入 node 引擎）
import json, os, re, sys, calendar as _cal

YTD_NAME = {3: '1Q', 6: '1H', 9: '9M'}        # 年初至今實際的標籤前綴（月數 → 前綴）
STUB_NAME = {3: '4Q', 6: '2H', 9: '2Q–4Q', 12: ''}  # 首期模型部分的標籤前綴（月數 → 前綴）
YTD_ALT = {3: 'Q1', 6: 'H1', 9: '9M'}         # 另一種寫法（例如「H1 借款」）
YTD_WORD = {3: '第 1 季', 6: '上半年', 9: '前三季'}
STUB_WORD = {3: '第 4 季', 6: '下半年', 9: '第 2–4 季', 12: '全年'}


def _add_months(y, m, k):
    t = y * 12 + (m - 1) + k
    return t // 12, t % 12 + 1


def _eom(y, m):
    return f'{y:04d}-{m:02d}-{_cal.monthrange(y, m)[1]:02d}'


def _fy_end(fy, fye):  # FYyy（財年結束所在的日曆年）→ (年, 月)
    return fy, fye


def _parse_q(s):
    m = re.fullmatch(r'FY(\d{2})Q([1-4])', s or '')
    if not m: raise ValueError(f'calendar：季度格式應為 FYyyQn，收到 {s!r}')
    return 2000 + int(m.group(1)), int(m.group(2))


def derive(co):
    c = co['calendar']
    fye, years, hz = int(c['fiscalYearEndMonth']), int(c['modelYears']), c['targetHorizon']
    assert 1 <= fye <= 12, 'calendar.fiscalYearEndMonth 應為 1–12'
    assert hz in ('firstFullYearEnd', 'valuationPlus12m'), f'calendar.targetHorizon 不支援：{hz}'
    if c.get('latestQuarterFiled'):
        fy, q = _parse_q(c['latestQuarterFiled'])
        ey, em = _fy_end(fy, fye)
        vy, vm = _add_months(ey, em, -3 * (4 - q))           # 已申報季的季末＝評價日
        ytd = 3 * q
        if q == 4: fy, ytd = fy + 1, 0                       # Q4（10-K）後：首期＝下一財年全年模型
    else:
        fy = 2000 + int(re.fullmatch(r'FY(\d{2})', c['firstModelFY']).group(1))
        vy, vm = _fy_end(fy - 1, fye); ytd = 0
    stub = 12 - ytd                                          # 首期模型部分的月數
    fys = [fy + i for i in range(years + 1)]
    ends = [_add_months(*_fy_end(f, fye), 0) for f in fys]
    mo = lambda y, m: (y - vy) * 12 + (m - vm)               # 評價日 → 某月底的月數
    t_end = [mo(*e) / 12 for e in ends]
    t_start = [0.0] + t_end[:-1]
    tgt_m = mo(*ends[1]) if hz == 'firstFullYearEnd' else 12
    ty, tm = _add_months(vy, vm, tgt_m)
    yy = lambda f: f'{f % 100:02d}'
    num = lambda x: int(x) if float(x).is_integer() else x  # 整數寫成 int（與舊版公式的常數寫法一致）
    out = {
        'fiscalYearEndMonth': fye, 'latestQuarterFiled': c.get('latestQuarterFiled'),
        'latestQuarterReported': c.get('latestQuarterReported'), 'targetHorizon': hz,
        'valuationDate': _eom(vy, vm), 'prevFYE': _eom(*_add_months(*_fy_end(fy - 1, fye), 0)), 'valuationMD': f'{vm}/{_cal.monthrange(vy, vm)[1]}',
        'ytdMonths': ytd, 'stubMonths': stub,
        'filedQLabel': (f"Q{c['latestQuarterFiled'][-1]} 20{c['latestQuarterFiled'][2:4]}" if c.get('latestQuarterFiled') else None),
        'ytdLabel': (YTD_NAME[ytd] + yy(fy)) if ytd else None,
        'ytdShort': YTD_NAME.get(ytd), 'ytdShortAlt': YTD_ALT.get(ytd), 'ytdWord': YTD_WORD.get(ytd),
        'stubShort': STUB_NAME[stub] or None, 'stubWord': STUB_WORD[stub],
        'stubLabel': (STUB_NAME[stub] + yy(fy)) if stub < 12 else f'FY{yy(fy)}',
        'periods': [f'FY{yy(f)}' for f in fys],
        'periodYears': [num(stub / 12)] + [1] * years,
        'periodEnd': [_eom(*e) for e in ends],
        'tEnd': [num(x) for x in t_end], 'tStart': [num(x) for x in t_start],
        'targetDate': _eom(ty, tm), 'targetT': num(tgt_m / 12),
        # EV/EBITDA 腿：錨定期 k（1..N）期末折回目標價時點的年數＝k − evOffset；evOffset＝目標價時點年數 − 首期長度
        'evOffset': num(tgt_m / 12 - stub / 12),
    }
    out['tokens'] = tokens(out)
    return out


def tokens(c):
    """期間字樣的佔位符 → 目前日曆的寫法（Excel 建置、cmp31、離線檢查共用）。程式中的說明文字以佔位符書寫，
    建置時統一換成目前日曆的字樣；目前日曆（FY26Q2 已申報）下換出的文字與 v4.4 完全相同。沒有年初至今實際數時以「年初至今」代稱。"""
    y, p = c['ytdMonths'], c['periods']
    na = '年初至今'
    return {
        '«VD»': c['valuationDate'], '«VMD»': c['valuationMD'], '«VSTART»': _next_day(c['valuationDate']),
        '«STUBEND»': c['periodEnd'][0][5:], '«STUBYR»': c['periodEnd'][0][:4], '«LASTYR»': c['periodEnd'][-1][:4],
        '«YTDL»': c['ytdLabel'] or na, '«YTDA»': c['ytdShortAlt'] or na, '«YTDW»': c['ytdWord'] or na, '«YTD»': c['ytdShort'] or na,
        '«STUBL»': c['stubLabel'], '«STUBW»': c['stubWord'], '«STUB»': c['stubShort'] or '全年',
        '«P0»': p[0], '«P1»': p[1], '«PL»': p[-1],
        '«PREVFYE»': c['prevFYE'], '«FYSTART»': _next_day(c['prevFYE']), '«VMMDD»': c['valuationDate'][5:], '«YTDQS»': '＋'.join(f'Q{i}' for i in range(1, y // 3 + 1)) or na,
        '«FY0»': f"{p[0]}＝{c['ytdShort']} 實際＋{c['stubWord']}模型" if y else f'{p[0]}＝全年模型',
    }


def _next_day(iso):
    import datetime as _dt
    return (_dt.date.fromisoformat(iso) + _dt.timedelta(days=1)).isoformat()


def fill(s, tk):
    """把字串中的佔位符換成目前日曆的字樣（長的先換，避免 «YTD» 吃掉 «YTDL»）。"""
    if not isinstance(s, str) or '«' not in s: return s
    for k in sorted(tk, key=len, reverse=True): s = s.replace(k, str(tk[k]))
    assert '«' not in s, f'未定義的期間佔位符：{s[:80]}'
    return s


def load(root=None):
    """讀 company.json、併入推算結果：periods、periodYears、valuation.optT 由日曆推算（company.json 不再存放）。"""
    root = root or os.path.dirname(os.path.abspath(__file__))
    co = json.load(open(os.path.join(root, 'company.json'), encoding='utf-8'))
    return apply(co)


def apply(co):
    cal = derive(co)
    for k in ('periods', 'periodYears'):
        assert k not in co, f'company.json 不應再有 {k}（v4.5 起由 calendar 推算）'
    assert 'optT' not in co['valuation'], 'company.json 不應再有 valuation.optT（v4.5 起＝評價日至模型期末的年數）'
    ya = co['ytdActual']
    assert ya.get('throughQuarter') == cal['latestQuarterFiled'], \
        f"ytdActual.throughQuarter（{ya.get('throughQuarter')}）須等於 calendar.latestQuarterFiled（{cal['latestQuarterFiled']}）"
    assert ya.get('months') == cal['ytdMonths'], f"ytdActual.months（{ya.get('months')}）須等於推算的年初至今月數 {cal['ytdMonths']}"
    if cal['ytdLabel']:
        assert co['historicalPL'][-1]['year'] == cal['ytdLabel'], f"historicalPL 最後一格（{co['historicalPL'][-1]['year']}）須為年初至今 {cal['ytdLabel']}"
        assert ya['label'].startswith(cal['ytdLabel']), f"ytdActual.label（{ya['label']}）須以 {cal['ytdLabel']} 開頭"
    co['cal'] = cal
    co['periods'], co['periodYears'] = cal['periods'], cal['periodYears']
    co['valuation']['optT'] = cal['tEnd'][-1]
    return co


if __name__ == '__main__':
    print(json.dumps(load(sys.argv[1] if len(sys.argv) > 1 else None)['cal'], ensure_ascii=False))
