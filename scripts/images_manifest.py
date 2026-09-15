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
    "260515-High-Price.png": "1억 넘는 요금이 설정된 상품이 있어야 한다. 임시 변경으로 만들면 그리드가 +130,00... 으로 잘린다. 억 축약은 셀 폭 때문에 있는 것이다",
    "260515-Mobile-Channel.png": "폰 프레임에 스크린샷 3장을 얹은 합성이다. 화면 하나가 아니라 디자인 작업이다",
    "260515-Mobile-Channel-Mapping.png": "같은 합성. 폰 프레임 3장",
    "260515-Billing-Cancel.png": "구독 취소 버튼을 눌러야 나온다. 구독/결제 버튼은 안 누른다",
    "260707-Inventory-Bulk-Update-1.png": "셀 드래그 복사는 CDP 로 재현이 안 된다(2026-09-14 재확인)",
    "260707-Inventory-Bulk-Update-2.png": "같은 이유. 주말만 드래그도 CDP 로 안 된다",
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
    "liveanywhere-min-nights-2.png": "최소 박수 개념을 설명하려고 그린 월 달력 도해다. VCMS 화면 캡처가 아니라 디자인 작업이다",
    "260609-Booking.png": "데스크톱 예약 상세와 폰 프레임을 나란히 얹은 합성이다. 화면 하나가 아니다",
    "image-14.png": "VCMS 아고다 연동 로그인 화면인데 아고다 채널 연결 버튼을 눌러야 나온다. 운영에서 채널 연결은 안 누른다",
    "image-28.png": "잘린 업장 이름을 툴팁으로 펼친 사진이다. 그 이름이 바로 가려야 하는 정보라 영어로 다시 찍어도 쓸 수 없다",
    "no-property-connected-label.png": "'연결한 숙소 없음' 배지 상태를 만들 수 없다. VENDIT HOTEL 은 연결 0, 대구 아르코는 6채널 전부 숙소가 붙어 있다",
    "Update-Note-Subscription-1.png": "유료 구독 상태 화면이다. 쓸 수 있는 업장 둘 다 무료 체험이고 구독 버튼은 안 누른다",
    "260724-distribution-free-trial-subscribe-2.png": "서비스 구독 모달이다. 구독 신청 버튼을 눌러야 나온다",
    "260724-subscription-free-plan-subscribe-2-1.png": "구독 구성 선택 모달. 같은 이유",
    "260724-subscription-paid-plan-manage-1-1.png": "유료 구독 상태가 필요하다",
    "260724-subscription-billing-date-change-1.png": "결제일 변경 모달. 결제 버튼은 안 누른다",
    "260724-subscription-paid-plan-manage-3-1.png": "구독 변경 모달. 같은 이유",
    "260724-subscription-payment-history-1-1.png": "결제 내역이 있어야 한다. 두 업장 다 0건(2026-09-14 확인)",
    "260724-subscription-payment-history-2.png": "결제 상세 모달. 같은 이유",
    "faq-no-history.png": "수집 시점에 이미 취소된 예약이 있어야 한다. VENDIT HOTEL 기본 조회 기간 Canceled 0건(2026-09-11)",
}

# 2026-09-14 대조 결과. 현재 빌드와 화면이 달라서 지금 다시 찍으면 그 릴리즈가 실제로
# 어떻게 생겼는지가 사라진다. Dean 결정: 과거 사진을 히스토리로 보존한다.
PRESERVE = {
    "change-scope-desktop.png": "현재 빌드는 상위 토글을 켜면 하위로 바로 내려간다. '하위 변경 항목' 팝오버가 없다",
    "change-scope-mobile.png": "같은 기능. 데스크톱에서 확인 단계가 사라졌다",
    "image-12.png": "판매 중지 확인 모달(개별 설정 유지)이 없다. 임시 변경 바로 바로 간다",
    "image-11.png": "판매 재개 확인 모달도 같이 없어졌다",
    "image-17.png": "요금 조절 모달이 Rate adjustment 로 전면 개편됐다. 평균 요금·초기화/저장 대신 OCC 배지·Amount/Percent·객실 타입 그룹",
    "image-25.png": "그리드 행 구성이 바뀌었다. 전체/판매 완료 → Availability/Sold/Adjustment/Check-in/out",
    "image-26.png": "채널 상품 정보 수정 모달이 없다. 수수료·전송가는 채널 > 숙소 정보로 옮겼다",
    "agoda-derived-1.png": "'이미 예약된 순 객실 박수' '예약 가능한 잔여 객실 박수' 행이 현재 그리드에 없다",
    "yanolja-channel-package-1.png": "채널 상품 정보 수정 모달이 없다(그리드 행·연필·링크·채널 상품 탭 다섯 경로 확인)",
    "agoda-channel-package-1.png": "같은 모달",
    "yeogi-channel-pacakge-1.png": "같은 모달",
    "Yanolja-Hardblock-1.png": "예약 표가 전면 개편됐다. 매출액 합계·제휴점 예약번호·상세보기·페이지네이션이 없고 카드/목록 전환이 생겼다",
    "package-fixed-rate-setting.png": "상품 생성 단계가 3개(기본 정보/요금 정보/기간별 요금 설정)에서 2개(Basic information/Rate plan)로 줄었다",
    "260617-Booking-Multiplier-Setting-2.png": "상품 생성 모달과 예약 상세가 둘 다 바뀐 합성이다",
    "Banner-Agoda-Referral-1.png": "아고다 입점 배너가 현재 빌드에 없다(채널·판매관리·숙박업소 목록 확인). 캠페인 배너라 내려간 것으로 본다",
    "260724-distribution-free-trial-subscribe-1-1.png": "판매관리 우상단 '무료 체험' 버튼이 제목 옆 배지로 바뀌었다",
    "260724-subscription-free-plan-subscribe-1-1.png": "구독 페이지 섹션이 기본 제공/이용 가능한 서비스 두 개에서 하나로 합쳐졌다",
}

# 릴리즈노트 본문에 박힌 채널 로고. images/ 루트에 있어서 channels/ 접두사 규칙에 안 걸린다.
CHANNEL_LOGOS = {
    "camfit.png", "Camperest-1.png", "banlife-stay.png", "liveanywhere-2.png",
}

# 릴리즈노트 안의 채널사 화면. 파일명만으로는 CHANNEL 정규식에 안 걸린다.
CHANNEL_SCREEN = {
    "260617-Booking-OTA-Example-2.png",
}

# 크롬 브라우저 자체 UI. VCMS 화면이 아니라 확장 프로그램 메뉴다.
BROWSER_UI = {
    "chrome-extension.png", "chrome-extension-1.png", "image-16.png",
}

# 찍을 수는 있는데 Dean 이 정해야 하는 것.
NEEDS_DEAN = {
    "Distribution-Booking-Sync-Only.png": "영어 배너가 {date} 를 그대로 찍는다. 값이 안 꽂히는 문제다. 2026-09-16 에 vcms-i18n origin/main 의 locales/latest/en.json 을 다시 열어봤는데 launchedAt 은 0건이고 app.sync-banner.description.* 는 여전히 {date} 다. 배포를 기다리면 풀린다고 적어놨던 건 틀렸다. 원인부터 다시 봐야 한다. en-distribution-booking-sync-only.png 는 준비돼 있다",
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
    if name.startswith("channels/") or name in CHANNEL_LOGOS:
        return "채널 로고 (언어 무관)"
    # 릴리즈노트 규칙이 여기 있었다. 그 자리에 있으면 뒤의 채널/로고/브라우저 판정이
    # 전부 "Dean 결정" 으로 덮여서, 범위 밖인 사진과 아직 안 찍은 사진이 한 칸에 섞였다.
    # 2026-09-09 결정은 Dean 이 "업데이트쪽도 수정가능한부분은 사진 교체" 로 뒤집었다(2026-09-13).
    if name in BLOCKED:
        return f"재현 불가 — {BLOCKED[name]}"
    if name in PRESERVE:
        return (f"한국어 보존 — {PRESERVE[name]}. "
                "지금 화면으로 다시 찍으면 그 릴리즈 기록이 아니게 된다(Dean, 2026-09-14)")
    if name in NEEDS_DEAN:
        return f"Dean 확인 필요 — {NEEDS_DEAN[name]}"
    if name in CHANNEL_CONNECTED:
        return ("재현 불가 — 채널 연결 플로우 중간 단계라 실제로 연결을 눌러야 나온다. "
                "운영 접근은 조회만 허용이라 못 찍는다(Dean, 2026-09-13)")
    if name in VCMS_OWN:
        return "영어 재캡처 필요"
    if name in BROWSER_UI:
        return "한국어 유지 — 크롬 브라우저 확장 프로그램 메뉴다. VCMS 화면이 아니다"
    if name in CHANNEL_SCREEN or CHANNEL.search(name) or "/channels/" in page \
            or "/faq/issue/" in page or CHANNEL_PAGE.search(os.path.basename(page)):
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
            if st.startswith(("영어 캡처 완료", "한국어 유지 —", "한국어 보존 —", "채널 로고")):
                done += 1
            body.append(f"| `{n}` | {st} |")
        body.append("")
    print(f"참조 {total}건 중 {done}건 정리 완료, {total - done}건 남음.")
    print()
    print("\n".join(body))


if __name__ == "__main__":
    main()
