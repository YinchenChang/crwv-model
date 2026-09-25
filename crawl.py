# 逐頁逐分頁擷取畫面文字（正規化版本號），用來比對兩版 HTML 的顯示結果是否完全相同
import sys, json, re
from playwright.sync_api import sync_playwright
def crawl(path):
    out = {}; errs = []
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto('file://' + path); pg.wait_for_timeout(2500)
        norm = lambda t: re.sub(r'v\d\.\d', 'vX', t)
        def snap(key): out[key] = norm(pg.inner_text('main') if pg.query_selector('main') else pg.inner_text('body'))
        for top in ['總結', '資金模型', '損益與評價']:
            pg.get_by_role('button', name=top, exact=True).click(); pg.wait_for_timeout(700); snap(top)
            seen = set()
            for _ in range(3):  # 兩層選單：逐一點擊可見的次級按鈕
                btns = [t for t in pg.locator('button:visible').all_inner_texts() if 0 < len(t) < 14]
                for t in btns:
                    if t in seen or t in ('總結','資金模型','損益與評價','簡報模式（全螢幕）','列印／另存 PDF','載入','重設','儲存 JSON','年度 CSV','站點 CSV') or t.startswith(('保守','基準','積極')): continue
                    seen.add(t)
                    try:
                        pg.get_by_role('button', name=t, exact=True).first.click(timeout=1500); pg.wait_for_timeout(400); snap(top + '/' + t)
                    except Exception: pass
        b.close()
    return out, errs
if __name__ == '__main__':
    o, e = crawl(sys.argv[1]); json.dump({'pages': o, 'errors': e}, open(sys.argv[2], 'w'), ensure_ascii=False); print(len(o), 'views; errors', e)
