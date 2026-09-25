// v4.3：重新產生 rv_snap.json（Excel「評價_反向DCF」與「摘要」頁引用的反向 DCF 快照）＝ HTML 引擎以 company.json 預設輸入計算 reverseDcf。
// 現價或任何預設輸入改變後執行：node scripts/rv_snap.js（以 v4.2 的檔案驗證過，輸出逐位元組相同）
const path = require('path'), fs = require('fs'), ROOT = path.join(__dirname, '..');
require(path.join(ROOT, 'load_engine.js'))(ROOT);
const r = reverseDcf(structuredClone(DEFAULTS), structuredClone(VAL_DEFAULTS));
const keys = ['price', 'baseDcf', 'baseTgt', 'R', 'C', 'Eb', 'Rt', 'caps', 'ebs', 'grid', 'rev30', 'util30', 'cost30', 'eb30'];
fs.writeFileSync(path.join(ROOT, 'rv_snap.json'), JSON.stringify(Object.fromEntries(keys.map(k => [k, r[k]]))));
console.log('rv_snap.json：price', r.price, 'R', r.R.toFixed(4), 'C', r.C.toFixed(4), 'Eb', r.Eb.toFixed(4), 'Rt', r.Rt.toFixed(4));
