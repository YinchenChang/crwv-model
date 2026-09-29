# 用語規則檢查（PR #12 第 6 輪；CLAUDE.md「用語規則」）：CLAUDE.md 用語表「不用」欄的詞，不得出現在
#   repo 的程式、文件（已存檔的 docs/reports 舊回報、dist/ 成品、預期差異清單 scripts/expect/、CLAUDE.md 用語表本身除外），
#   以及本次建置的成品（HTML 的畫面文字與程式、Excel 所有儲存格的字串與公式）。
# 用法：python3 scripts/check_terms.py [建置的 .html／.xlsx ...]
import sys, os, re, subprocess, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
md = open(os.path.join(ROOT, 'CLAUDE.md'), encoding='utf-8').read()
sec = md.split('## 用語規則', 1)[1].split('\n## ', 1)[0]
BAN = [m.group(1).strip() for m in re.finditer(r'^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*$', sec, re.M)
       if m.group(1).strip() not in ('不用', '---')]
assert BAN, 'CLAUDE.md「用語規則」表格讀不到'
SKIP = ('docs/reports/', 'dist/', 'scripts/expect/', 'docs/baseline_', 'docs/template_')
hits = []
files = subprocess.run(['git', 'ls-files'], cwd=ROOT, capture_output=True, text=True).stdout.split('\n')
for f in files:
    if not f or f.startswith(SKIP) or not f.endswith(('.py', '.js', '.md', '.json', '.sh', '.txt')): continue
    t = open(os.path.join(ROOT, f), encoding='utf-8', errors='ignore').read()
    if f == 'CLAUDE.md': t = t.replace(sec, '')
    hits += [(f, w) for w in BAN if w in t]
for p in sys.argv[1:]:
    if p.endswith('.xlsx'):
        z = zipfile.ZipFile(p)
        t = ''.join(z.read(n).decode('utf-8', 'ignore') for n in z.namelist() if n.endswith('.xml'))
    else:
        t = open(p, encoding='utf-8', errors='ignore').read()
    hits += [(os.path.basename(p), w) for w in BAN if w in t]
if hits:
    print('用語規則：以下檔案仍使用「不用」欄的詞：'); [print(f'  {f}：{w}') for f, w in hits]; sys.exit(1)
print(f'用語規則：{len(BAN)} 個舊用語，repo 與成品皆未出現')
