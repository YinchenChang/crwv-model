# 用法：python3 build_html_portable.py <版本> <輸出路徑> <日期> <模板 HTML>
# 模板可用任一版已發布的 HTML（例如 20260923_CoreWeave收支模型_v3_3.html），只取其中的 React／Recharts 函式庫部分。
import sys, os
H = os.path.dirname(os.path.abspath(__file__))
ver, out, date, tpl = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
L = open(os.path.join(H, 'app_pretty.js'), encoding='utf-8').read().split('\n')
rng = lambda a, b: '\n'.join(L[a-1:b])
mid1 = rng(686, 2518); mid2 = rng(2941, 2976); mid3 = rng(3650, 3751)
mid3 = mid3.replace("var NM = [`年度假設`, `年度結果`, `收入／容量`, `成本`, `信用`, `終值`, `園區`, `敏感性`, `連動檢查`, `來源`];",
                    "var NM = [`支出假設`, `各期結果`, `收入／產能`, `電力成本`, `信用／利率`, `終值`, `站點`, `敏感性`, `連動檢查`, `來源與承諾`, `債務明細`];")
k = mid3.index('function RM('); ke = mid3.find('\nfunction ', k + 10); ke = len(mid3) if ke < 0 else ke
mid3 = mid3[:k] + open(os.path.join(H, 'rm_andy.js'), encoding='utf-8').read().rstrip('\n') + mid3[ke:]
seg = lambda n: open(os.path.join(H, n), encoding='utf-8').read()
import json as _json
_co = _json.load(open(os.path.join(H, 'company.json'), encoding='utf-8'))  # 公司資料單一來源
# 注意：模板函式庫在插入點前是一個未結束的 var 宣告鏈（…,Rk=…,），所以第一個敘述必須是「名稱 = 值」接續該鏈
app = '\n'.join(['COMPANY_DATA = ' + _json.dumps(_co, ensure_ascii=False) + ';', seg('segA.js'), mid1, seg('segB.js'), mid2, seg('segC.js'), mid3, seg('segD.js'), seg('tail.js'), seg('segE.js')])
s = open(tpl, encoding='utf-8').read()
i = -1
for _mk in ('COMPANY_DATA = {"meta"', 'zk=[`FY27`', 'zk = [`FY26`'):  # v4.0 起以 var CO 為起點；相容舊模板
    i = s.find(_mk)
    if i >= 0: break
j = s.find('</script>', i)
html = s[:i] + app + s[j:]
import re
html = re.sub(r'<!-- .*?-->', f'<!-- Backlog 不是現金 · CoreWeave 收支模型 v{ver}（更新 {date}）· 雙擊以 Chrome / Edge 開啟，不需安裝或連網 -->', html, count=1)
html = re.sub(r'<title>.*?</title>', f'<title>Backlog 不是現金 · CoreWeave 收支模型 v{ver} · {date} · 離線版</title>', html, count=1)
tag = ver.replace('.', '')
html = html.replace('`v`, `1.0`', f'`v`, `{ver}`').replace('crwv_annual_v10', f'crwv_annual_v{tag}').replace('crwv_sites_v10', f'crwv_sites_v{tag}').replace('crwv_model_v10', f'crwv_model_v{tag}')
open(out, 'w', encoding='utf-8').write(html)
print('built', len(html))
