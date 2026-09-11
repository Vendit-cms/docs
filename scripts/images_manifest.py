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

# 채널 FAQ 페이지. 이미지가 image-34.png 처럼 이름만으로는 채널 화면인지 모른다.
CHANNEL_PAGE = re.compile(r"^(airbnb|yanolja|agoda|expedia|naver|tripcom|yeogi)", re.I)

# 다시 못 찍는 이유. 확인한 것만 적는다.
BLOCKED = {
    "edit-roomtype-confirm.png": "CMS 관리 객실타입 + 범위를 벗어난 연결 상품이 필요하다",
    "일괄변경_4.png": "임시 변경 바는 일괄변경이 아니라 셀 직접 수정 플로우 것이다",
    "일괄변경_5.png": "임시 변경 바는 일괄변경이 아니라 셀 직접 수정 플로우 것이다",
    "Inviting-1.png": "대기 중인 초대가 실재해야 한다",
    "booking_scaleFactor.png": "배수가 걸린 예약 두 건을 나란히 놓은 합성이다",
    "create-pkg-inclusions.png": "현재 빌드 상품 모달에 서비스 선택이 없다. 서비스는 요금에 붙는다(en-rate-inclusions). 문서가 낡았다",
    "cancel-booking-noti.png": "카카오 알림톡 원문이다. 한국어로만 발송된다",
    "faq-no-history.png": "수집 시점에 이미 취소된 예약이 있어야 한다. VENDIT HOTEL 기본 조회 기간 Canceled 0건(2026-09-11)",
}

# 찍을 수는 있는데 Dean 이 정해야 하는 것.
NEEDS_DEAN = {
    "Distribution-Booking-Sync-Only.png": "영어 배너가 {date} 를 그대로 찍는다. dev 번들 en.json 이 낡았고 vcms-i18n main 은 {launchedAt} 로 고쳐져 있다. en-distribution-booking-sync-only.png 준비됨, 배포 후 교체",
    "pkg_delete.png": "현재 빌드는 휴지통이 비활성으로 안 바뀐다. 눌러서 뜨는 대화상자를 찍어야 하는데 운영 삭제 버튼이라 자동 모드가 막았다",
    "연동서비스_4.png": "VCLOUD 해제 대화상자. 해제 버튼을 여는 동작이라 자동 모드가 막았다",
    "연동서비스_2.png": "VCLOUD 연동 입력 모달. dev 에서 Connect 를 여는 동작도 자동 모드가 막았다",
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
    if "/release-notes/" in page:
        return "한국어 재사용 (Dean 결정, 2026-09-09)"
    if name in BLOCKED:
        return f"재현 불가 — {BLOCKED[name]}"
    if name in NEEDS_DEAN:
        return f"Dean 확인 필요 — {NEEDS_DEAN[name]}"
    if CHANNEL.search(name) or "/channels/" in page or "/faq/issue/" in page \
            or CHANNEL_PAGE.search(os.path.basename(page)):
        return "채널사 화면 — Dean 이 직접 촬영"
    return "한국어 유지 — 영어 재캡처 필요"


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
            if st.startswith("영어") or st.startswith("한국어 재사용") or st.startswith("채널 로고"):
                done += 1
            body.append(f"| `{n}` | {st} |")
        body.append("")
    print(f"참조 {total}건 중 {done}건 정리 완료, {total - done}건 남음.")
    print()
    print("\n".join(body))


if __name__ == "__main__":
    main()
