#!/usr/bin/env python3
"""IMAGES.md 를 en/ 의 실제 참조에서 다시 만든다.

손으로 고치면 금방 낡는다. 캡처를 한 묶음 끝낼 때마다 이걸 돌려라.

    python3 scripts/images_manifest.py > IMAGES.md
"""
import collections
import os
import re
import unicodedata as ud

CHANNEL = re.compile(
    r"채널_|야놀자|아고다|여기어때|익스피디아|에어비앤비|airbnb|expedia|naver|camfit|Camfit"
    r"|camperest|트립비토즈|리브애니웨어|chrome-extension|크롬확장|KakaoTalk|260727-channel",
    re.I)

# VCMS 자체 화면인데 파일명(채널_*)이나 페이지 위치(faq/issue) 때문에 채널사 화면으로 잘못 세던 것.
# 2026-09-12 썸네일로 하나씩 확인했다. 우리가 찍는다.
VCMS_OWN = {
    "채널_연결완료-2.png", "채널_연결가능-1.png", "채널_연결-1.png", "channel-property-info-none-connected.png", "channel-property-connect-1.png",
    "채널_숙소정보.png", "채널_예약수수료율.png", "채널_채널전송가.png", "채널_채널상품.png", "채널_채널상품_정보수정.png",
    "채널_채널상품_상품숨김.png", "채널_2-3.png", "채널_3-2.png", "채널_17(1).png", "채널_13(1).png", "채널_14(1).png",
    "채널_22(2).png", "채널_15(2).png", "채널_수수료_2-1.png", "채널_수수료_3-1.png", "채널_17.png", "채널_22.png", "채널_23.png",
    "image(67).png", "yanolja-system-error-modal-1.png", "설정_숙박업소_알림연락처-2.png", "notification.png",
}

# 연결된 채널이 있어야 찍히는 화면. 2026-09-13 에 20장을 대구 아르코(연결 채널 6개)에서 조회만으로 찍었다.
# 남은 두 장은 실제로 연결 버튼을 눌러야 나오는 단계라, 조회 전용 권한으로는 못 만든다.
CHANNEL_CONNECTED = {
    "channel-property-info-none-connected.png", "channel-property-connect-1.png",
}

# 채널 FAQ 페이지. 이미지가 image-34.png 처럼 이름만으로는 채널 화면인지 모른다.
CHANNEL_PAGE = re.compile(r"^(airbnb|yanolja|agoda|expedia|naver|tripcom|yeogi)", re.I)

# 다시 못 찍는 이유. 확인한 것만 적는다.
BLOCKED = {
    "260820-rate-drag-2.png": "셀 드래그 복사는 CDP 로 재현이 안 된다. mousePressed/mouseMoved/mouseReleased 를 쏴도 복사 메뉴가 안 뜬다(2026-09-14 재확인)",
    "260820-timetable-drag.png": "같은 이유. 입퇴실 시간 드래그도 CDP 로 안 된다",
    "260820-scale-factor-disabled.png": "객실이 1개인 객실 타입이 있어야 예약 배수가 비활성으로 뜬다. VENDIT HOTEL 최소 객실 타입이 2개다",
    "edit-roomtype-confirm.png": "CMS 관리 객실타입 + 범위를 벗어난 연결 상품이 필요하다",
    "bulk-edit-4.png": "임시 변경 바는 일괄변경이 아니라 셀 직접 수정 플로우 것이다",
    "bulk-edit-5.png": "임시 변경 바는 일괄변경이 아니라 셀 직접 수정 플로우 것이다",
    "Inviting-1.png": "대기 중인 초대가 실재해야 한다",
    "booking_scaleFactor.png": "배수가 걸린 예약 두 건을 나란히 놓은 합성이다",
    "create-pkg-inclusions.png": "현재 빌드 상품 모달에 서비스 선택이 없다. 서비스는 요금에 붙는다(en-rate-inclusions). 문서가 낡았다",
    "cancel-booking-noti.png": "카카오 알림톡 원문이다. 한국어로만 발송된다",
    "channel-auto-disconnect-noti.png": "카카오 알림톡 원문이다. 한국어로만 발송된다",
    "integration-vcloud-2.png": "찍을 필요 없음. VCLOUD 는 점주가 설정 못 하게 막아둔 게 의도다(Dean, 2026-09-12). 한국어 가이드도 같은 관리자 매뉴얼 절을 갖고 있다",
    "integration-vcloud-4.png": "찍을 필요 없음. VCLOUD 는 점주가 설정 못 하게 막아둔 게 의도다(Dean, 2026-09-12)",
    "notification.png": "채널 상품 알림이 있어야 한다. VENDIT HOTEL 은 알림 0건이고, dev 는 여는 순간 읽음 처리될 수 있어서 안 열었다(2026-09-12)",
    "yanolja-system-error-modal-1.png": "야놀자 장애 때만 뜨는 모달이라 재현 불가",
    "faq-no-history.png": "수집 시점에 이미 취소된 예약이 있어야 한다. VENDIT HOTEL 기본 조회 기간 Canceled 0건(2026-09-11)",
}

# 크롬 브라우저 자체 UI. VCMS 화면이 아니라 확장 프로그램 메뉴다.
BROWSER_UI = {
    "chrome-extension.png", "chrome-extension-1.png",
}

# 찍을 수는 있는데 Dean 이 정해야 하는 것.
NEEDS_DEAN = {
    "Distribution-Booking-Sync-Only.png": "영어 배너가 {date} 를 그대로 찍는다. dev 번들 en.json 이 낡았고 vcms-i18n main 은 {launchedAt} 로 고쳐져 있다. en-distribution-booking-sync-only.png 준비됨, 배포 후 교체",
    "pkg_delete.png": "현재 빌드는 휴지통이 비활성으로 안 바뀐다. 눌러서 뜨는 대화상자를 찍어야 하는데 운영 삭제 버튼이라 자동 모드가 막았다",
}


def scan():
    pages = collections.defaultdict(list)
    for root, _, files in os.walk("en"):
        for f in sorted(files):
            if not f.endswith(".mdx"):
                continue
            p = os.path.join(root, f)
            text = open(p, encoding="utf-8").read()
            seen = []
            # 파일명에 \( \) 로 이스케이프된 괄호가 있다(image-\(1\).png). 그 앞에서 끊기면 안 된다.
            for m in re.findall(r'/images/((?:\\.|[^\s"\')<>\\])+)', text):
                name = ud.normalize("NFC", m).replace("\\", "")
                if name not in seen:
                    seen.append(name)
            if seen:
                pages[p] = seen
    return pages


def status(name, page):
    if name.startswith("en-"):
        return "영어 캡처 완료"
    if name.startswith("channels/"):
        return "채널 로고 (언어 무관)"
    # BLOCKED 를 릴리즈노트 규칙보다 먼저 본다. 안 그러면 못 찍는 이유가
    # "Dean 결정" 으로 덮여서 왜 안 됐는지 기록이 사라진다.
    if name in BLOCKED:
        return f"재현 불가 — {BLOCKED[name]}"
    if "/release-notes/" in page:
        return "한국어 재사용 (Dean 결정, 2026-09-09)"
    if name in NEEDS_DEAN:
        return f"Dean 확인 필요 — {NEEDS_DEAN[name]}"
    if name in CHANNEL_CONNECTED:
        return ("재현 불가 — 채널 연결 플로우 중간 단계라 실제로 연결을 눌러야 나온다. "
                "운영 접근은 조회만 허용이라 못 찍는다(Dean, 2026-09-13)")
    if name in VCMS_OWN:
        return "영어 재캡처 필요"
    if name in BROWSER_UI:
        return "한국어 유지 — 크롬 브라우저 확장 프로그램 메뉴다. VCMS 화면이 아니다"
    if CHANNEL.search(name) or "/channels/" in page or "/faq/issue/" in page \
            or CHANNEL_PAGE.search(os.path.basename(page)):
        return ("한국어 유지 — 채널사가 만든 화면이라 범위 밖이다. "
                "본문 영어 번역만 하고 사진은 한국어 그대로 둔다(Dean, 2026-09-13)")
    return "영어 재캡처 필요"


def main():
    pages = scan()
    total = done = 0
    print("# 영어 문서 이미지 현황")
    print()
    print("`scripts/images_manifest.py` 가 en/ 의 실제 참조를 읽어 만든다. 손으로 고치지 마라.")
    print()
    print("`en-` 로 시작하는 파일은 영어 UI 에서 새로 찍은 것이다. 나머지는 한국어 원본을 그대로 쓴다.")
    print("`images/` 는 한국어 문서와 공유하므로 원본을 덮으면 한국어까지 바뀐다. 그래서 새 파일로 넣는다.")
    print()
    body = []
    for page, names in sorted(pages.items()):
        body.append(f"## `{page}`")
        body.append("")
        body.append("| 이미지 | 상태 |")
        body.append("| --- | --- |")
        for n in names:
            st = status(n, page)
            total += 1
            if st.startswith(("영어 캡처 완료", "한국어 재사용", "한국어 유지 —", "채널 로고")):
                done += 1
            body.append(f"| `{n}` | {st} |")
        body.append("")
    print(f"참조 {total}건 중 {done}건 정리 완료, {total - done}건 남음.")
    print()
    print("\n".join(body))


if __name__ == "__main__":
    main()
