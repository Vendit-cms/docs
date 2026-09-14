#!/usr/bin/env python3
"""영어 캡처에서 사이드바가 통째로 날아갔는지 본다.

    python3 scripts/check_captures.py

2026-09-13 에 채널 캡처 9장이 사이드바 없이 배포됐다. 원인은 내부 메뉴를 가리는
`HIDE_INTERNAL` 이 부모를 3단계 무조건 올라가서 nav 를 통째로 숨긴 것이다.
사람 눈으로는 모달만 보고 넘어가기 쉬웠다. 그래서 기계로 센다.

판정은 왼쪽 사이드바 영역의 명암 표준편차다. 메뉴 글자가 있으면 값이 크고,
흰 바탕만 남으면 0 에 가깝다. 사이드바가 원래 없는 화면은 SKIP 에 적어둔다.
"""
import os
import subprocess
import sys

IMAGES = "images"
# 사이드바가 원래 없는 화면. 로그인 화면과 잘라낸 범례 조각.
SKIP = {
    "en-signin-email.png", "en-signin-phone.png",
    "en-legend-availability-2.png", "en-legend-change-status-2.png",
    "en-legend-rate-adjustment.png", "en-legend-rate-status-2.png",
    "en-legend-sell-status-2.png",
    # 2026-09-14 릴리즈노트 재촬영. 사이드바가 원래 안 들어가는 것들.
    "en-fixed-rate-protection.png",     # 그리드 셀 몇 개만 잘라낸 조각
    "en-room-type-settings.png",        # 모달 두 장을 화살표로 이은 합성
    "en-rate-period-settings.png",      # 모달만 잘라냄
    "en-booking-date-filters.png",      # 드롭다운 조각
    "en-bulk-update-selection.png",     # 모달 안 조각
    "en-bulk-update-date-range.png",    # 모달 안 조각
}
CROP = "330x1200+20+420"   # 사이드바 메뉴가 있어야 할 자리
FLOOR = 2.0                # 이 아래면 빈 것으로 본다


def sidebar_ink(path):
    r = subprocess.run(
        ["magick", path, "-crop", CROP, "+repage", "-colorspace", "Gray",
         "-format", "%[fx:standard_deviation*100]", "info:"],
        capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return None


def main():
    bad, checked = [], 0
    for f in sorted(os.listdir(IMAGES)):
        if not f.startswith("en-") or not f.endswith(".png") or f in SKIP:
            continue
        sd = sidebar_ink(os.path.join(IMAGES, f))
        if sd is None:
            continue
        checked += 1
        if sd < FLOOR:
            bad.append((f, sd))
    print(f"영어 캡처 {checked}장 검사 · 사이드바 빈 것 {len(bad)}장")
    for f, sd in bad:
        print(f"  {f}  sd={sd:.2f}")
    if bad:
        print("\n다시 찍어라. scripts/capture_redacted.py 로 찍으면 사이드바가 남는다.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
