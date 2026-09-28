# 以 v4.5 xlsx 的公式建立依賴圖，計算各「目標輸出」的前導格集合（精簡版至少要保留的格）
import openpyxl, re, sys, json
from openpyxl.formula import Tokenizer
from openpyxl.utils import range_boundaries, get_column_letter
from openpyxl.worksheet.formula import DataTableFormula
P='dist/20260926_CoreWeave收支模型_v4_5.xlsx'
wb=openpyxl.load_workbook(P)
def cells_of(sheet, ref):
    ref=ref.replace('$','')
    if ':' in ref:
        c1,r1,c2,r2=range_boundaries(ref)
    else:
        c1,r1,c2,r2=range_boundaries(ref+':'+ref)
    return [(sheet,r,c) for r in range(r1,r2+1) for c in range(c1,c2+1)]
deps={}; kind={}
for ws in wb.worksheets:
    for row in ws.iter_rows():
        for x in row:
            v=x.value; k=(ws.title,x.row,x.column)
            if v is None: continue
            if isinstance(v,DataTableFormula):
                kind[k]='f'; deps[k]=None; continue
            if isinstance(v,str) and v.startswith('='):
                kind[k]='f'; ds=[]
                for t in Tokenizer(v).items:
                    if t.type=='OPERAND' and t.subtype=='RANGE':
                        s=t.value
                        if '!' in s:
                            sh,rf=s.rsplit('!',1); sh=sh.strip("'")
                        else: sh,rf=ws.title,s
                        try: ds+=cells_of(sh,rf)
                        except Exception: pass
                deps[k]=ds
            else:
                kind[k]='t' if isinstance(v,str) else 'n'
# 模擬運算表（輸入與假設 D166:E168）：每格＝以情境 1/2/3 重算整個模型，依賴公式列 D165:E165 與情境輸入格 C5
for r in (166,167,168):
    for c in (4,5):
        deps[('輸入與假設',r,c)]=[('輸入與假設',165,4),('輸入與假設',165,5),('輸入與假設',5,3),('輸入與假設',r,3)]
        kind[('輸入與假設',r,c)]='f'
def closure(targets):
    seen=set(); st=list(targets)
    while st:
        k=st.pop()
        if k in seen: continue
        seen.add(k)
        for d in deps.get(k) or []: st.append(d)
    return seen
def rng(sh,ref): return cells_of(sh,ref)
T={
 'G1 三情境目標價與評等': rng('評價_DCF與目標價','C48:D70')+rng('摘要','C5:D15'),
 'G2 資金缺口與股權稀釋': rng('各期收支','C39:G41')+rng('各期收支','C58:G70'),
 'G3 共識與指引差異及原因': rng('摘要','C17:E48')+rng('摘要','C51:C54'),
 'G4 季度追蹤（焦點季）': rng('摘要','C61:G67'),
 'G5 反向 DCF 摘要': rng('摘要','C55:E58'),
}
allk=set(); out={}
for n,t in T.items():
    s=closure(t); allk|=s
    f=sum(1 for k in s if kind.get(k)=='f'); i=sum(1 for k in s if kind.get(k)=='n')
    out[n]=(f,i,len({k[0] for k in s if k in kind}))
    print(n,'公式',f,'數值輸入',i,'涉及分頁',sorted({k[0] for k in s if k in kind}))
F=sum(1 for k,v in kind.items() if v=='f'); N=sum(1 for v in kind.values() if v=='n')
fa=sum(1 for k in allk if kind.get(k)=='f'); na=sum(1 for k in allk if kind.get(k)=='n')
print('全部 公式',F,'數值',N,'｜聯集 公式',fa,'數值',na)
per={}
for k,v in kind.items():
    d=per.setdefault(k[0],[0,0,0,0])
    if v=='f': d[0]+=1; d[1]+= k in allk
    if v=='n': d[2]+=1; d[3]+= k in allk
for s,d in per.items(): print(s,'公式 %d→%d 數值 %d→%d'%tuple(d))
# 單獨看目標價（G1）：不在 G1 前導集合內的公式數＝可刪而不改目標價
g1=closure(T['G1 三情境目標價與評等'])
print('G1 以外的公式',F-sum(1 for k in g1 if kind.get(k)=='f'))
print('----- 輸入與假設 各列：是否在聯集／G1 內')
ws=wb['輸入與假設']
for r in range(1,ws.max_row+1):
    ks=[('輸入與假設',r,c) for c in range(3,9) if ('輸入與假設',r,c) in kind and kind[('輸入與假設',r,c)]!='t']
    if not ks: continue
    a=str(ws.cell(r,1).value)[:38]
    print(r,a,'| U' if any(k in allk for k in ks) else '| -','G1' if any(k in g1 for k in ks) else '--', [ws.cell(r,c).value for c in range(3,5)])
print('----- 精簡版估計：保留列的 A 欄標籤字數')
rows={(k[0],k[1]) for k in allk if k in kind}
lab=0; nrows=0; per2={}
for (s,r) in rows:
    v=wb[s].cell(r,1).value
    if isinstance(v,str) and not v.startswith('='):
        lab+=len(v); nrows+=1; per2[s]=per2.get(s,0)+1
print('保留列',len(rows),'標籤字數',lab, per2)
tr=sum(wb[s].max_row for s in wb.sheetnames); print('全部列',tr)
