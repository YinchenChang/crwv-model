#!/usr/bin/env bash
# 一次跑完建置與核對：建 HTML → 建 Excel → 重算 → fix_outline → fix_datatable → verify_ooxml → 三情境 xlx＋cmp31 → FY27 錨定 cmp31。
# 任何一項失敗即以非零代碼結束。產物放在 repo 根目錄的 out/（不納入版控）。
# 用法：scripts/verify.sh [--vs-dist]
#   --vs-dist  另與 dist/ 內現行成品比對：crawl.py 畫面文字與 xl_diff.py --values 皆須 0 差異（純結構修改的驗收）。
# 版本號與更新日：預設取 vlog.py 最後一列與 dist/ 成品檔名的日期；可用環境變數 VER、DATE 覆寫。
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/out"
mkdir -p "$OUT"
cd "$ROOT"
export LC_ALL=C.UTF-8 LANG=C.UTF-8

VS_DIST=0
[[ "${1:-}" == "--vs-dist" ]] && VS_DIST=1

VER="${VER:-$(python3 -c "import vlog; print(vlog.VLOG[-1][0].lstrip('v'))")}"
DIST_HTML="$(ls dist/*_v*.html | head -1)"
DIST_XLSX="$(ls dist/*_v*.xlsx | head -1)"
DATE_TAG="$(basename "$DIST_HTML" | cut -d_ -f1)"           # 20260924
DATE="${DATE:-${DATE_TAG:0:4}-${DATE_TAG:4:2}-${DATE_TAG:6:2}}"  # 2026-09-24
NAME="${DATE//-/}_CoreWeave收支模型_v${VER//./_}"
HTML="$OUT/$NAME.html"
XLSX="$OUT/$NAME.xlsx"

PASS=(); FAIL=()
step() { echo; echo "=== $1"; }
ok()   { PASS+=("$1"); echo "[PASS] $1"; }
bad()  { FAIL+=("$1"); echo "[FAIL] $1"; }
finish() {
  echo; echo "================ 結果 ================"
  for s in "${PASS[@]}"; do echo "PASS  $s"; done
  for s in "${FAIL[@]:-}"; do [[ -n "$s" ]] && echo "FAIL  $s"; done
  if (( ${#FAIL[@]} )); then echo "verify.sh：失敗 ${#FAIL[@]} 項"; exit 1; fi
  echo "verify.sh：全部通過（${#PASS[@]} 項）"; exit 0
}

# cmp31 輸出中 OK 行數、XX／MISSING 行數；有任何不一致即失敗
run_cmp() {  # $1=標籤 $2..=cmp31 參數
  local label="$1"; shift
  local log="$OUT/cmp31_${label}.log"
  if ! (cd "$OUT" && node "$ROOT/cmp31.js" "$@") > "$log" 2>&1; then bad "cmp31 $label（執行錯誤，見 $log）"; return; fi
  local nok nbad
  nok=$(grep -c '^OK ' "$log" || true)
  nbad=$(grep -cE '^(XX |MISSING)|\| MISSING XL KEY' "$log" || true)
  if (( nbad == 0 && nok > 0 )); then ok "cmp31 $label：$nok 項全部 OK"
  else bad "cmp31 $label：OK $nok、不一致 $nbad（見 $log）"; grep -E '^(XX |MISSING)|MISSING XL KEY' "$log" | head -10; fi
}

step "1. 建 HTML（v$VER · $DATE）"
if python3 build_html_portable.py "$VER" "$HTML" "$DATE" docs/template_v3_3.html; then ok "建 HTML"; else bad "建 HTML"; finish; fi

step "2. 建 Excel"
if python3 build_xlsx.py "$XLSX"; then ok "建 Excel"; else bad "建 Excel"; finish; fi

step "3. 重算（LibreOffice headless）"
if python3 scripts/recalc.py "$XLSX" 120; then ok "重算：0 公式錯誤"; else bad "重算"; finish; fi

step "4. fix_outline"
if python3 fix_outline.py "$XLSX"; then ok "fix_outline"; else bad "fix_outline"; finish; fi

step "4b. fix_datatable（模擬運算表還原為 Excel 格式）"
if python3 fix_datatable.py "$XLSX"; then ok "fix_datatable"; else bad "fix_datatable"; finish; fi

step "5. verify_ooxml"
if python3 verify_ooxml.py "$XLSX"; then ok "verify_ooxml：OOXML OK"; else bad "verify_ooxml"; fi

step "6. 三情境 xlx＋cmp31（預設錨定）"
declare -A SC=([1]=low [2]=base [3]=high)
for s in 1 2 3; do
  if python3 xlx.py "$XLSX" "$s" "$OUT/xl17_$s.json"; then run_cmp "${SC[$s]}" "${SC[$s]}"
  else bad "xlx 情境 $s"; fi
done

step "7. FY27 錨定 cmp31（基準）"
if python3 xlx.py "$XLSX" 2 "$OUT/xl17_2_a1.json" 1; then run_cmp "base_FY27" base 1
else bad "xlx FY27 錨定"; fi

if (( VS_DIST )); then
  step "8. 與 dist/ 成品比對"
  python3 crawl.py "$DIST_HTML" "$OUT/crawl_dist.json"
  python3 crawl.py "$HTML" "$OUT/crawl_new.json"
  if python3 - "$OUT/crawl_dist.json" "$OUT/crawl_new.json" <<'EOF'
import sys, json, difflib
a, b = (json.load(open(p)) for p in sys.argv[1:3])
pa, pb = a['pages'], b['pages']
n = sum(len(v) for v in pa.values())
diff = [k for k in sorted(set(pa) | set(pb)) if pa.get(k) != pb.get(k)]
print(f'畫面：dist {len(pa)} 個、新版 {len(pb)} 個頁面／分頁，約 {n:,} 字；差異 {len(diff)} 個；頁面錯誤 dist {len(a["errors"])}、新版 {len(b["errors"])}')
for k in diff[:5]:
    print('  ', k); print('\n'.join(list(difflib.unified_diff((pa.get(k) or '').splitlines(), (pb.get(k) or '').splitlines(), lineterm='', n=0))[:12]))
sys.exit(1 if diff or b['errors'] or not pa else 0)
EOF
  then ok "crawl 畫面文字 0 差異"; else bad "crawl 畫面文字"; fi
  r=$(python3 xl_diff.py "$DIST_XLSX" "$XLSX" --values); echo "$r"
  if [[ "$(head -1 <<<"$r")" == "0 differences" ]]; then ok "xl_diff --values 0 差異"; else bad "xl_diff --values"; fi
  r=$(python3 xl_diff.py "$DIST_XLSX" "$XLSX"); echo "$r"
  if [[ "$(head -1 <<<"$r")" == "0 differences" ]]; then ok "xl_diff 公式 0 差異"; else bad "xl_diff 公式"; fi
fi

finish
