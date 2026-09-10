#!/usr/bin/env bash
# 캡처 전용 크롬 프로필을 열어 로그인만 해 둔다. 1회만 하면 된다.
# 이 프로필은 캡처에만 쓰이고, 평소 쓰는 크롬 프로필과 완전히 분리돼 있다.
set -euo pipefail
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PROFILE="${VCMS_CAPTURE_PROFILE:-$HOME/.vcms-capture-profile}"
mkdir -p "$PROFILE"
echo "크롬 창이 뜬다. 다음을 하고 창을 닫아라:"
echo "  1. vcms.io 로그인 (VENDIT HOTEL 계정)"
echo "  2. 헤더의 지구본 아이콘 > English 선택"
echo "  3. 창 닫기"
"$CHROME" --user-data-dir="$PROFILE" --no-first-run --no-default-browser-check \
  --window-size=1440,900 "https://vcms.io" 
