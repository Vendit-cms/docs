#!/usr/bin/env bash
# 개발 서버(development.vcms.io) 로그인을 캡처 프로필에 심는다. 1회만.
#
# 운영에는 없는 화면(구독 상세, 결제 수단, 연결된 채널)을 dev 에서 찍으려고 쓴다.
# dev 는 조회만 한다 - 저장 버튼은 누르지 않는다. [[vcms-server-access-boundary]]
set -euo pipefail
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PROFILE="${VCMS_CAPTURE_PROFILE:-$HOME/.vcms-capture-profile}"
mkdir -p "$PROFILE"
rm -f "$PROFILE/SingletonLock"
echo "크롬 창이 뜬다. 다음을 하고 창을 닫아라:"
echo "  1. development.vcms.io 로그인"
echo "  2. 구독이 살아 있고 채널이 연결된 업소를 고른다"
echo "  3. 헤더 지구본 아이콘 > English"
echo "  4. 주소창의 accommodations/<ID> 를 복사해서 나한테 준다"
echo "  5. 창 닫기"
"$CHROME" --user-data-dir="$PROFILE" --no-first-run --no-default-browser-check \
  --window-size=1440,900 "https://development.vcms.io"
