#!/bin/bash
# Claude Code 雲端環境的 Setup script（貼到環境設定的 Setup script 欄位；結果會被快取）
set -e
apt-get update -y
apt-get install -y --no-install-recommends libreoffice-calc fonts-noto-cjk   # Excel 重算＋中文字型
pip install --break-system-packages openpyxl pypdf playwright
python3 -m playwright install --with-deps chromium                           # 畫面比對（crawl.py）用
