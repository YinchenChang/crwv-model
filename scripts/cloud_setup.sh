#!/bin/bash
# Claude Code 雲端環境 Setup script（v2）
# 官方限制：約 5 分鐘內結束、且必須以 0 結束，否則工作階段無法啟動。
# 因此：兩組安裝並行、各自設時間上限、失敗不中斷；缺少的工具由 Claude 在工作階段內補裝（見 CLAUDE.md 第 0 步）。
LOG=/var/log/crwv_setup.log
exec > >(tee -a "$LOG") 2>&1
echo "setup start $(date)"
export DEBIAN_FRONTEND=noninteractive

# 1) LibreOffice（Excel 重算用；nogui 版較小，不裝字型）
( timeout 240 apt-get update -y -q && \
  timeout 240 apt-get install -y -q --no-install-recommends libreoffice-calc-nogui ) \
  || echo "WARN: LibreOffice 未安裝完成" &

# 2) Python 套件與 Playwright 的 Chromium（畫面比對 crawl.py 用）
( timeout 120 pip install -q --break-system-packages openpyxl pypdf playwright && \
  timeout 150 python3 -m playwright install chromium ) \
  || echo "WARN: Python 套件或 Chromium 未安裝完成" &

wait
command -v soffice >/dev/null && echo "OK: soffice" || echo "MISSING: soffice"
python3 -c "import openpyxl, playwright" 2>/dev/null && echo "OK: python pkgs" || echo "MISSING: python pkgs"
echo "setup end $(date)"
exit 0
