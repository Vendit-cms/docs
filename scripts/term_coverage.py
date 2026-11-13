#!/usr/bin/env python3
"""ko 페이지에 실제로 쓰인 용어가 en 페이지에 canon 영어로 나타나는지 대조한다.

blocklist 검사(glossary_check.py)는 내가 상상한 오역만 잡는다. 이 검사는 반대다.
원문에 등장한 용어를 전부 훑으므로 상상하지 못한 누락도 걸린다.

정본
    vcms-i18n/glossary/glossary.json        135 항목, PM 결정 note 포함
    vcms-i18n/locales/latest/{ko,en}.json   3,278 키, 실제 화면 문자열

긴 용어부터 마스킹한다. 그러지 않으면 '숙박업소' 안의 '숙박' 을 잡아 잡음만 나온다.

    python3 scripts/term_coverage.py                 # glossary 만 (기본)
    python3 scripts/term_coverage.py --with-locales  # locales 까지
"""
import json, os, re, sys

I18N = os.path.expanduser("~/projects/vcms-i18n")
STOP_KO = {"전체", "확인", "취소", "저장", "설정", "삭제", "선택", "적용", "닫기", "없음", "사용",
           "시간", "날짜", "이름", "정보", "목록", "상태", "변경", "추가", "수정", "검색", "등록",
           "조회", "완료", "실패", "오류", "안내", "필수", "일", "월", "년", "개", "명"}


def load(with_locales=False):
    terms, notes = {}, {}

    def add(ko, en, note=""):
        if not ko or not en or len(ko) < 2 or ko in STOP_KO:
            return
        if not re.search(r"[가-힣]", ko) or len(ko) > 14:
            return
        if re.search(r"[{}<>%\d]", ko):
            return
        terms.setdefault(ko, set()).add(en.strip())
        if note and ko not in notes:
            notes[ko] = note

    g = json.load(open(f"{I18N}/glossary/glossary.json", encoding="utf-8"))
    for t in g["terms"]:
        add(t.get("ko"), t.get("en"), t.get("note", ""))

    if with_locales:
        ko = json.load(open(f"{I18N}/locales/latest/ko.json", encoding="utf-8"))
        en = json.load(open(f"{I18N}/locales/latest/en.json", encoding="utf-8"))

        def flat(d, p=""):
            for k, v in d.items():
                n = f"{p}.{k}" if p else k
                if isinstance(v, dict):
                    yield from flat(v, n)
                else:
                    yield n, v
        K, E = dict(flat(ko)), dict(flat(en))
        for k, v in K.items():
            if isinstance(v, str) and isinstance(E.get(k), str):
                add(v, E[k])
    return terms, notes


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


# ---- 오탐 걸러내기 (2026-11-14, 68건 전수 대조 뒤 추가) --------------------------
# 68건을 ko 줄과 en 줄을 나란히 놓고 봤더니 번역 누락은 0건이었고 전부 아래 세 갈래였다.
# 새 예외를 넣을 땐 근거(i18n 키나 실제 문장)를 주석으로 단다. 근거 없으면 넣지 마라.

# 1) 제품 자신이 canon 말고 쓰는 영어. 낱말 첫머리에서만 맞춘다(link -> linked, links).
ALT_EN = {
    "서비스": ["Inclusion"],        # glossary note: inclusion 맥락은 en 만 Inclusion. audits.domain.inclusion 등 39키
    "연결": ["Link", "Map"],        # common.affected-package.empty "No linked packages" 22키, bookings.action.map-package 33키
    "퇴실": ["Check-in/out"],       # inventories.label.check-in-out-time: 입/퇴실 시간 -> Check-in/out
    "결제": ["Pay", "Paid"],        # 동사로 쓴 "결제돼요". 명사 Payment 로는 못 옮긴다
    "구독": ["Subscribed"],         # accommodation.main.status.subscribing: 구독 중 -> Subscribed
    "결제 완료": ["Complete"],      # 상태 라벨(Completed)이 아닌 "결제 완료 시" 문장. en: when a payment completes
    "해지": ["Cancel"],             # payments.label.cancel-scheduled "Cancellation scheduled", ...snackbar.canceled 등 20키
}

# 2) 글자만 같고 다른 말인 한국어. 대조 전에 가린다.
KO_SKIP = [
    r"판매가 (?=시작|멈|중지|중단|불가)",   # 판매 + 조사 가. "판매가 중지돼요" 는 Sell rate 가 아니다
    r"(?<=[가-힣])해지(?=[고지며면는])",    # 정해지고, 또렷해지고. 구독 해지가 아니다
    r"예약자",                              # bookings.column.name: 예약자 -> Guest name. Booking 이 아니다
    r"아동 숙박 허용 여부",                 # 아고다 YCS 메뉴명(Allow children). 채널사 화면이라 용어집 밖
    r"가맹이? 해지",                        # 네이버 가맹 해지(partnership terminated). 구독 해지가 아니다
]

# 3) 그 쪽 그 문장에서 영어가 명사를 풀어 쓴 자리. (용어, en 경로) 로만 연다.
PAGE_OK = {
    ("상품", "en/channels/camfit.mdx"): "계약된 상품이라 -> is contracted with a partner company",
    ("금액", "en/channels/channel-setting.mdx"): "적용된 금액에서 -> on top of what Distribution applied",
    ("연결", "en/release-notes/2026-01-14.mdx"): "객실타입에 연결된 상품 -> packages on a room type",
    ("연결", "en/release-notes/2026-07-07.mdx"): "연결된 하위 상품 -> the packages below",
}


def en_has(en_terms, et, alts=()):
    """et 는 norm() 된 영어 본문. canon 은 예전처럼 부분 일치, 여기에 복수형과 띄어쓰기 차이를 더 받는다."""
    tight = et.replace(" ", "")
    for e in en_terms:
        n = norm(e)
        if not n:
            continue
        if n in et:
            return True
        if n.endswith("y") and n[:-1] + "ies" in et:      # Property -> properties
            return True
        if n.replace(" ", "") in tight:                   # Yanoljapension -> Yanolja pension
            return True
    for a in alts:
        if re.search(r"(?<![a-z0-9])" + re.escape(norm(a)), et):
            return True
    return False


def mask_ko(ko_text):
    for pat in KO_SKIP:
        ko_text = re.sub(pat, lambda m: "@" * len(m.group(0)), ko_text)
    return ko_text


def missing(ko_text, en_text, terms, ep=""):
    et = norm(en_text)
    out = []
    for term in present(mask_ko(ko_text), terms):
        if en_has(terms[term], et, ALT_EN.get(term, ())):
            continue
        if (term, ep) in PAGE_OK:
            continue
        out.append(term)
    return out


def selftest(terms):
    """검사기가 오탐은 놓아주고 진짜 누락은 여전히 잡는지. 2026-11-14 Dean "오탐 고쳐"."""
    cases = [
        # (ko, en, 잡혀야 하는 용어)
        ("객실을 열면 바로 판매가 시작돼요.", "Sales start right away.", set()),
        ("요금이 먼저 정해지고 버튼이 또렷해지고", "The rate is set first.", set()),
        ("재고 관리만 쓰는 숙소는", "For properties that use Inventory only", set()),
        ("에어비앤비, 야놀자 펜션은", "On Airbnb and Yanolja pension", set()),
        ("| 입/퇴실 시간 | O | X |", "| Check-in/out | O | X |", set()),
        ("### 서비스 목록", "### Inclusion list", set()),
        ("기간을 상품에 연결해 주세요.", "Link the period to your packages.", set()),
        ("실제 예약자 사이트에는", "the guest-facing site", set()),
        # 아래는 진짜 누락이다. 예외를 넓히다 이게 통과하면 검사기가 죽은 것이다.
        ("판매가를 올려요.", "Raise the selling price.", {"판매가"}),
        ("구독을 해지해요.", "Stop using it.", {"해지"}),
        ("판매가 기준으로 계산해요.", "Calculated from the price.", {"판매가"}),
        ("숙소 정보를 확인해요.", "Check the accommodation info.", {"숙소"}),
        ("서비스 목록", "Option list", {"서비스"}),
        ("채널을 연결해요.", "Attach the channel.", {"연결"}),
        ("퇴실 시간", "Leaving time", {"퇴실"}),
        ("가맹이 해지되면 연결을 끊어요.", "If the partnership is terminated, VCMS disconnects it.", set()),
        ("일부 서비스 해지가 예정된", "some services are scheduled for cancellation", set()),
    ]
    bad = []
    for ko, en, want in cases:
        got = set(missing(ko, en, terms))
        # want 가 비면 아무것도 안 잡혀야 하고, 있으면 그 용어가 잡혀야 한다
        if (not want and got) or (want and not want <= got):
            bad.append((ko, en, sorted(want), sorted(got)))
    return bad


def present(ko_text, terms):
    """긴 용어부터 소비해서, 짧은 용어가 긴 용어 안에서 잡히지 않게 한다."""
    t, hit = ko_text, []
    for term in sorted(terms, key=len, reverse=True):
        if term in t:
            hit.append(term)
            t = t.replace(term, "@" * len(term))
    return hit


def main():
    with_loc = "--with-locales" in sys.argv
    terms, notes = load(with_loc)
    bad = selftest(terms if not with_loc else load(False)[0])   # 자가검사는 늘 glossary 사전으로
    if bad:
        print("자가검사 실패: 검사기 규칙이 깨졌다")
        for ko, en, want, got in bad:
            print(f"    ko={ko!r} en={en!r} 기대={want} 실제={got}")
        sys.exit(2)
    miss, pairs = [], 0
    for r, _, fs in os.walk("ko"):
        for f in fs:
            if not f.endswith(".mdx"):
                continue
            kp = os.path.join(r, f)
            ep = "en" + kp[2:]
            if not os.path.exists(ep) or "/reference/" in ep:
                continue
            pairs += 1
            kt = open(kp, encoding="utf-8").read()
            for term in missing(kt, open(ep, encoding="utf-8").read(), terms, ep):
                miss.append((term, ep))
    by = {}
    for term, ep in miss:
        by.setdefault(term, []).append(ep)
    src = "glossary + locales" if with_loc else "glossary"
    print(f"용어 사전 {len(terms)}개 ({src}) | 대조 {pairs}쌍 | 누락 {len(miss)}건, 용어 {len(by)}개")
    print()
    for term, eps in sorted(by.items(), key=lambda x: -len(x[1])):
        note = notes.get(term, "")
        print(f"{term:14} -> {sorted(terms[term])[:2]}  {len(eps):>2}쪽  {note[:52]}")
        print(f"    {eps[0]}")
    sys.exit(1 if miss else 0)


if __name__ == "__main__":
    main()
