PERIOD_LABELS = PERIODS, // 接續模板片段 mid1 結尾未結束的宣告鏈，所以不可加 var
  HIST_PL = COMPANY_DATA.historicalPL,
  VAL_DEFAULTS = structuredClone(COMPANY_DATA.valuation),
  lM = [{
    ticker: `NBIS`,
    name: `Nebius Group`,
    role: `Neocloud 直接對標`,
    mkt: 63.81,
    netDebt: 2.16,
    ev: 65.97,
    rev: 1.36,
    opl: 0,
    ebitda: -.194,
    asOf: `EBITDA：FY25 20-F`,
    note: `GAAP 營業損失 −0.612＋D&A 0.418（FY2025；季報 6-K 未 XBRL 標註，無法算 TTM）。營收為 TTM 1.36`
  }, {
    ticker: `IREN`,
    name: `IREN Limited`,
    role: `Neocloud／自建電力`,
    mkt: 18.61,
    netDebt: 1.7,
    ev: 20.31,
    rev: .707,
    opl: .003,
    ebitda: -.629,
    asOf: `FY26 10-K（6/30）`,
    note: `GAAP 營業損失 −1.047＋D&A 0.418。自有電廠、營業租賃負債僅 0.003bn`
  }, {
    ticker: `APLD`,
    name: `Applied Digital`,
    role: `房東（Polaris Forge）`,
    mkt: 8.22,
    netDebt: 3.37,
    ev: 11.59,
    rev: .6113,
    opl: .066,
    ebitda: -.169,
    asOf: `FY26 10-K（5/31）`,
    note: `GAAP 營業損失 −0.236＋D&A 0.067。租約多未起租，EBITDA 尚未反映 36bn 合約`
  }, {
    ticker: `CORZ`,
    name: `Core Scientific`,
    role: `房東（高密度託管）`,
    mkt: 5.9,
    netDebt: 2.53,
    ev: 8.43,
    rev: .4403,
    opl: .109,
    ebitda: -.498,
    asOf: `TTM 至 Q2（6/30）`,
    note: `GAAP 營業損失 −0.561＋D&A 0.063。託管轉型期`
  }];

function uM(e, t) {
  return t ? e / t - 1 : 0
}

function dM(e) {
  return Math.max(0, -e)
}
var fM = .035;

function shareCount(e, t) {
  let n = e.includeAtm ? 0 : fM;
  return Math.max(.1, t.shares - n)
}

function mM(e, t, n) {
  return Math.max(0, e - t / Math.max(n, .01))
}

function mR(e, t, n) {
  return e - t / Math.max(n, .01)
}

function forwardPL(e, t) {
  let n = HIST_PL[2],
    r = n.revenue,
    s = t.shares,
    sb = t.shares,
    N = t.nol ?? 0,
    N2 = t.nol ?? 0;
  return PERIOD_LABELS.map((n, c) => {
    let L = PERIOD_YEARS[c],
      l = e.years[c].isRev,
      u = e.years[c].servicesRev,
      d = l + u,
      f = c === 0 ? uM(HIST_PL[3].revenue + d, r) : uM(d, r),
      EB = d * e.years[c].ebM,
      p = EB - e.years[c].daFleet,
      m = e.years[c].interest,
      pt = p - m,
      tb = Math.max(0, pt - Math.min(N, Math.max(0, pt) * .8)),
      tx = tb * t.tax,
      h = pt - tx;
    pt < 0 ? N += -pt : N -= Math.min(N, pt * .8);
    sb = c === 0 ? t.shares : sb * 1.01, s = sb + (e.years[c].cumNewShares || 0);
    let g = h / s,
      _ = (h + t.sbc * L) / s,
      v = e.years[c].daFleet,
      y = e.years[c].cashCapex,
      b = .02 * Math.max(0, d - r),
      tb2 = Math.max(0, p - Math.min(N2, p * .8)),
      x = p - tb2 * t.tax + v - y - b,
      S = e.years[c].revenue,
      w = e.years[c].newRev,
      T = e.years[c].capacity > 0 ? e.years[c].unsold / e.years[c].capacity : 0,
      E = p + v;
    return N2 -= Math.min(N2, p * .8), r = c === 0 ? HIST_PL[3].revenue + d : d, {
      fyRevenue: c === 0 ? HIST_PL[3].revenue + d : d,
      fyOpInc: c === 0 ? HIST_PL[3].opInc + p : p,
      fyNi: c === 0 ? HIST_PL[3].ni + h : h,
      fyDa: c === 0 ? ACTUAL_1H.da + v : v,
      fyEbitda: c === 0 ? HIST_PL[3].opInc + ACTUAL_1H.da + EB : EB,
      fyEps: c === 0 ? HIST_PL[3].eps + h / s : h / s,
      fyNgEps: c === 0 ? HIST_PL[3].ngEps + (h + t.sbc * L) / s : (h + t.sbc * L) / s,
      year: n,
      gpu: l,
      services: u,
      revenue: d,
      fundingRev: S,
      inYear: w,
      plugRatio: T,
      yoy: f,
      opInc: p,
      opM: p / d,
      ebitda: E,
      ni: h,
      tax: tx,
      nm: h / d,
      eps: g,
      ngEps: _,
      shares: s,
      da: v,
      cashCapex: y,
      interest: m,
      ufcf: x
    }
  })
}

function ncdfQ(x) {
  let t = 1 / (1 + .2316419 * Math.abs(x)),
    d = .3989423 * Math.exp(-x * x / 2),
    p = d * t * (.3193815 + t * (-.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274))));
  return x > 0 ? 1 - p : p
}

function bsCallQ(S, K, T, r, s) {
  if (S <= 0) return 0;
  if (K <= 0) return S;
  let d1 = (Math.log(S / K) + (r + s * s / 2) * T) / (s * Math.sqrt(T)),
    d2 = d1 - s * Math.sqrt(T);
  return S * ncdfQ(d1) - K * Math.exp(-r * T) * ncdfQ(d2)
}

function dcfValue(e, t) {
  let n = e.map(e => e.ufcf),
    r = n.map((e, n) => e / (1 + t.wacc) ** (n + .5)),
    i = r.reduce((e, t) => e + t, 0),
    c = e[e.length - 1],
    l = c.opInc * (1 - t.tax) + c.da - c.da * t.maintRatio,
    bad = t.wacc <= t.g ? `WACC ≤ 永續成長率，Gordon 終值無定義` : l <= 0 ? `常態化 FCF ≤ 0，終值無經濟意義` : ``,
    a = bad ? 0 : l * (1 + t.g) / (t.wacc - t.g),
    o = a / (1 + t.wacc) ** 4.5,
    s = i + o,
    u = s - t.netDebt,
    q = t.fund ? t.fund.eq.reduce((e, n, r) => e + n / (1 + t.wacc) ** Math.max(0, r - .5), 0) : 0,
    z = t.shares + (t.fund ? t.fund.sh : 0),
    zr = Math.max(0, (u + q) / z),
    op = bsCallQ(s + q, t.netDebt, t.optT ?? 4.5, t.rf ?? .04, t.sigma ?? .5) / z,
    ps = bad ? NaN : (t.dcfMode === `option` ? op : zr);
  return {
    invalid: !!bad,
    invalidReason: bad,
    zeroPerShare: zr,
    optPerShare: op,
    pvFcf: i,
    tv: a,
    pvTv: o,
    ev: s,
    equity: u,
    pvEquityRaised: q,
    postShares: z,
    perShare: ps,
    perShareRaw: (u + q) / z,
    tvShare: o / Math.max(Math.abs(s), 1) * Math.sign(s || 1),
    normFcf: l,
    fcf: n,
    pv: r
  }
}

function evEbitdaLeg(e, t) {
  // v3.5：(錨定年 EBITDA × 倍數 − 錨定年末淨負債) ÷ 錨定年末股數，再以 WACC 折回 FY27 末（目標價時點）
  let k = Math.min(4, Math.max(1, Math.round(t.evYear ?? 1))),
    n = t.fund ? t.fund.ndY[k] : t.netDebt,
    r = t.fund ? e[k].shares : t.shares; // 損益股數：SBC 逐年複利稀釋＋瀑布新股（FY27 與 v3.4 相同）
  return (e[k].ebitda * t.evEbitda - n) / r / Math.pow(1 + t.wacc, k - 1)
}
// v3.5：錨定年度 × 倍數矩陣（加權目標價與 EV/EBITDA 腿，均為每股）
var EVG_MULTS = [3.4, 4.5, 5, 6, 7];
function evAnchorGrid(d, st, o) {
  let base = runValuation(d, st, o);
  let leg = EVG_MULTS.map(m => [1, 2, 3, 4].map(k => {
    let y = d.years[k];
    return Math.max(0, (base.fwd[k].ebitda * m - (y.totalDebtEnd - y.cum)) / base.fwd[k].shares / Math.pow(1 + o.wacc, k - 1))
  }));
  let DI = base.d.invalid, wd = DI ? 0 : BLEND_W.dcf, dcf = DI ? 0 : base.d.perShare;
  return {
    mults: EVG_MULTS,
    years: [1, 2, 3, 4].map(k => d.years[k].year),
    leg: leg,
    tgt: leg.map(r => r.map(x => wd * dcf + (1 - wd) * x)),
    dcf: dcf,
    wd: wd
  }
}
var BLEND_W = COMPANY_DATA.methodology.blendWeights,
  bM = [{
    method: `DCF（融資後每股）`,
    capex: `已扣五期 Cash CapEx；終值用常態化 FCF（D&A×維持比率）`,
    hole: `不扣缺口：新債視為公允價值、價值中性；新股募得現金折現後加回，股數同步增加`,
    shares: `含 ATM ＋ 瀑布新股`,
    netDebt: `6/30 本金 35.55 − 現金 5.54 = 30.0`
  }, {
    method: `EV/EBITDA（錨定年度，可選 FY27–FY30）`,
    capex: `EBITDA 未扣 CapEx`,
    hole: `不扣缺口：改用錨定年末淨負債（含瀑布新債）與股數（含瀑布新股）；FY28 起以 WACC 折回 FY27 末`,
    shares: `錨定年末（含 SBC 稀釋與新股）`,
    netDebt: `錨定年末總債務 − 現金`
  }]

function blendCall(e) {
  let {
    spot: t,
    dcfPx: n,
    pePx: i,
    eqTotal: a,
    newSh: q,
    tvShare: o,
    mktCap: M,
    shares0: S0,
    dcfInvalid: DI
  } = e, WD = DI ? 0 : BLEND_W.dcf, WE = 1 - WD, s = (DI ? 0 : WD * n) + WE * i, c = s / Math.max(t, .01) - 1, u = a <= .01, B = a > 1.5 * M, d = [];
  u ? d.push(`融資狀態：五期缺口可全由債務（額度＋資產層新債，受 債務／backlog 上限約束）支應，不需新股。`) : d.push(`融資狀態：五期需股權募資 ${a.toFixed(0)}bn（約現市值 ${(a/Math.max(M,1)).toFixed(1)} 倍），新發行 ${q.toFixed(2)}bn 股，原股東最終持股約 ${(S0/(S0+q)*100).toFixed(0)}%。股權在需要前一期募足（期前融資），不再以缺口本金扣減估值。`), B && d.push(`股權募資超過現市值 1.5 倍：市場吸收能力存疑，禁止買進。`), o > .85 && d.push(`終值占企業價值過高，DCF 對 WACC／永續成長／維持性 CapEx 比率極敏感。`);
  let f = c >= .25 && o < .9 && !B ? `買進` : c <= -.15 || B && c <= -.08 ? `賣出` : `中立`;
  DI && d.unshift(`DCF 失效，已排除於目標價（權重改為 EV/EBITDA 100%）。`);
  let p = (DI ? i : Math.min(n, i)) * .9,
    m = (DI ? i : Math.max(n, i)) * 1.05;
  return {
    blended: s,
    upside: c,
    call: f,
    lo: p,
    hi: m,
    notes: d,
    hole: a,
    funded: u,
    blocked: B,
    weights: {
      dcf: WD,
      pe: WE
    },
    dcfInvalid: DI
  }
}

function dcfGridWaccG(e, t) {
  let n = [.09, .1, .11, .12, .13];
  return [.02, .025, .03, .035, .04].map(r => n.map(n => n <= r ? NaN : dcfValue(e, {
    ...t,
    wacc: n,
    g: r
  }).perShare))
}
function wM(e) {
  let t = [...e].filter(e => Number.isFinite(e)).sort((e, t) => e - t),
    n = Math.floor(t.length / 2);
  return t.length ? t.length % 2 ? t[n] : (t[n - 1] + t[n]) / 2 : NaN
}

function runValuation(e, t, n) {
  let r = shareCount(t, n),
    Y2 = e.years,
    i = {
      ...n,
      shares: r,
      fund: {
        eq: Y2.map(e => e.equity || 0),
        sh: e.totals.newShares || 0,
        sh27: Y2[1].cumNewShares || 0,
        nd27: Y2[1].totalDebtEnd - Y2[1].cum,
        shY: Y2.map(e => e.cumNewShares || 0),
        ndY: Y2.map(e => e.totalDebtEnd - e.cum)
      }
    },
    a = forwardPL(e, i),
    o = dcfValue(a, i),
    c = evEbitdaLeg(a, i),
    d = Math.max(0, c),
    f = blendCall({
      spot: i.price,
      dcfPx: o.perShare,
      pePx: d,
      eqTotal: e.totals.equity || 0,
      newSh: e.totals.newShares || 0,
      tvShare: o.tvShare,
      mktCap: i.price * r,
      shares0: r,
      dcfInvalid: o.invalid
    });
  return {
    v: i,
    fwd: a,
    d: o,
    peRaw: c,
    peAdj: d,
    hole: e.totals.equity || 0,
    fullHole: e.totals.equity || 0,
    nd27: i.fund.nd27,
    sh27: r * 1.01 + i.fund.sh27,
    evK: Math.min(4, Math.max(1, Math.round(i.evYear ?? 1))),
    ndA: i.fund.ndY[Math.min(4, Math.max(1, Math.round(i.evYear ?? 1)))],
    shA: a[Math.min(4, Math.max(1, Math.round(i.evYear ?? 1)))].shares,
    call: f,
    shares: r
  }
}

function EM(e, t, n) {
  let r = e.fwd[1],
    i = r.services,
    a = Math.abs(r.revenue - (r.gpu + i)) < .05,
    o = e.fwd.every((e, n) => Math.abs(e.cashCapex - t.years[n].cashCapex) < 1e-6),
    s = e.fwd.every((e, n) => Math.abs(e.interest - t.years[n].interest) < 1e-6),
    c = !e.call.blocked || e.call.call !== `買進`,
    l = n.includeAtm || e.shares < VAL_DEFAULTS.shares - .01,
    h = e.fwd[0].revenue * 2,
    g = h + 0;
  return [{
    id: `val-cap`,
    ok: a,
    severity: a ? `ok` : `block`,
    title: `營收連動產能`,
    detail: `FY27 算力產能 ${r.gpu.toFixed(1)} + 非算力服務 ${i.toFixed(1)} = 營收 ${r.revenue.toFixed(1)}bn。改 Billable／利用率／rev/MW 會改這列。`
  }, {
    id: `val-capex`,
    ok: o,
    severity: o ? `ok` : `block`,
    title: `DCF Cash CapEx 連動`,
    detail: `五期 Cash CapEx ${t.totals.cashCapex.toFixed(0)}bn 與損益／DCF 為同一組數字。`
  }, {
    id: `val-int`,
    ok: s,
    severity: s ? `ok` : `block`,
    title: `利息連動`,
    detail: `損益表利息（存量債務利息＋現金為負時的透支利息 ${t.totals.overdraft.toFixed(1)}bn、CDS 連動加碼）取自資金模型。`
  }, {
    id: `val-veto`,
    ok: c,
    severity: c ? e.call.funded ? `ok` : `watch` : `block`,
    title: `股權募資過大禁止買進`,
    detail: e.call.funded ? `五期缺口可全由債務支應，無需新股。` : `五期需股權 ${e.hole.toFixed(0)}bn；${e.call.blocked ? `超過現市值 1.5 倍，結論不會是買進` : `未超過現市值 1.5 倍`}。結論「${e.call.call}」。`
  }, {
    id: `val-atm`,
    ok: l,
    severity: `ok`,
    title: `ATM／可轉債與股數`,
    detail: n.includeAtm ? `含 ATM 上限 35m 股，評價股數 ${e.shares.toFixed(3)}bn（7/31 流通 0.5515bn）。2033 可轉債潛在 37.8m 股（轉換價 $97.85，capped call 至 $199.70）未計入。` : `ATM 關閉，股數由 ${VAL_DEFAULTS.shares.toFixed(3)} 扣回 35m 股為 ${e.shares.toFixed(3)}bn，缺口同步擴大。`
  }, {
    id: `val-rev-guide`,
    ok: (HIST_PL[3].revenue + e.fwd[0].revenue) >= 12.4 - .05,
    severity: (HIST_PL[3].revenue + e.fwd[0].revenue) >= 12.4 ? `ok` : `watch`,
    title: `2026 營收指引 $12.4–13.2bn`,
    detail: `法說上修全年 12.4–13.2、Q3 3.45–3.6。本模型 1H 實際 4.653 + 2H26 IS ${e.fwd[0].revenue.toFixed(2)} = ${(HIST_PL[3].revenue+e.fwd[0].revenue).toFixed(2)}bn。調整後營業利益指引 0.96–1.15；模型 2H26 GAAP 營業利益 ${e.fwd[0].opInc.toFixed(2)}（未加回 SBC）。`
  }, {
    id: `val-plug`,
    ok: r.plugRatio <= .2,
    severity: r.plugRatio > .2 ? `watch` : `ok`,
    title: `IS 與資金模型同一組營收`,
    detail: `FY27 算力營收 ${r.gpu.toFixed(1)} = 期初 RPO 轉換 ${r.fundingRev.toFixed(1)} + 新簽約 ${r.inYear.toFixed(1)}；未售產能占容量 ${(r.plugRatio*100).toFixed(0)}%。非算力服務 ${r.services.toFixed(1)} 單列。新簽約收入取決於「新產能簽約率」，是 Assumed；超過 20% 未售會標示。`
  }, {
    id: `dcf-validity`,
    ok: !e.d.invalid,
    severity: e.d.invalid ? `watch` : `ok`,
    title: e.d.invalid ? `DCF 失效：${e.d.invalidReason}` : `DCF 有效（WACC − g ＝ ${((e.v.wacc - e.v.g)*100).toFixed(1)}%，常態化 FCF ${e.d.normFcf.toFixed(1)}）`,
    detail: `失效只定義為數學上的失效：WACC ≤ g，或常態化 FCF ≤ 0。股權價值為負不算失效——那是有效的經濟結論（企業價值低於淨負債）。目前下限方式：${e.v.dcfMode === `option` ? `選擇權（Merton，σ ${(e.v.sigma*100).toFixed(0)}%）` : `0 截斷`}；0 截斷 $${e.d.zeroPerShare.toFixed(1)}、選擇權 $${e.d.optPerShare.toFixed(1)}。失效時 DCF 權重歸零、EV/EBITDA 權重 100%。`
  }, {
    id: `val-double`,
    ok: !0,
    severity: `ok`,
    title: `舉債與股權的分工（期前融資瀑布）`,
    detail: `v1.9 以前假設缺口 100% 舉債且無上限：透支利息是借款的利息，扣 NTM 缺口是借款的本金（即 FY27 末增加的淨負債），兩者是同一筆借款的利息與本金，並非重複計費。v2.0 的差別在於新債受 債務／backlog 上限約束，超出部分改以股權按現價折價募集：股權沒有利息、也不增加淨負債，但增加股數。在全額舉債的設定下（上限放到極大），v2.0 的基準目標價約 $17，與 v1.9 的 $19.5 一致。`
  }]
}
