#!/usr/bin/env bash
# Dean 이 직접 몰 크롬 창을 띄운다. 캡처 프로필을 그대로 쓰고 디버깅 포트를 열어 둔다.
# 이 창에서 원하는 화면을 띄워 놓으면 python3 scripts/shoot_now.py <이름.png> 로 그대로 찍는다.
set -euo pipefail
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PROFILE="${VCMS_CAPTURE_PROFILE:-$HOME/.vcms-capture-profile}"
PORT="${CDP_PORT:-9222}"
URL="${1:-https://www.vcms.io}"
mkdir -p "$PROFILE"
rm -f "$PROFILE/SingletonLock"
exec "$CHROME" --user-data-dir="$PROFILE" --no-first-run --no-default-browser-check \
  --remote-debugging-port="$PORT" --window-size=1440,900 --window-position=0,0 "$URL"
