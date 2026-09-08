#!/usr/bin/env bash
# VCMS 화면을 원본급 해상도로 캡처한다.
# 사전 준비(1회): scripts/capture-login.sh 를 실행해 캡처 전용 프로필에 로그인해 둔다.
set -euo pipefail

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PROFILE="${VCMS_CAPTURE_PROFILE:-$HOME/.vcms-capture-profile}"
OUT="${2:-/tmp/vcms-capture.png}"
URL="${1:?usage: capture.sh <url> [out.png] }"
W="${W:-1440}"
H="${H:-900}"
SCALE="${SCALE:-3}"   # 1440 * 3 = 4320px, 원본(4096) 이상

if [ ! -d "$PROFILE" ]; then
  echo "캡처 프로필이 없다: $PROFILE" >&2
  echo "먼저 scripts/capture-login.sh 를 실행해 로그인해라." >&2
  exit 1
fi

rm -f "$OUT"
"$CHROME" --headless=new --disable-gpu --no-first-run --no-default-browser-check \
  --user-data-dir="$PROFILE" \
  --window-size="${W},${H}" --force-device-scale-factor="$SCALE" \
  --hide-scrollbars --virtual-time-budget=8000 \
  --screenshot="$OUT" "$URL" >/dev/null 2>&1 &

# 크롬은 스크린샷을 쓰고도 안 죽는다. 파일이 생기면 끝난 것으로 본다.
for _ in $(seq 1 60); do
  [ -s "$OUT" ] && break
  sleep 0.5
done
pkill -f "user-data-dir=$PROFILE" >/dev/null 2>&1 || true

if [ ! -s "$OUT" ]; then echo "캡처 실패: $URL" >&2; exit 1; fi
echo "$OUT $(sips -g pixelWidth -g pixelHeight "$OUT" | awk '/pixel/{printf "%s ", $2}')"
