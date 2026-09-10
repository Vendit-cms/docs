#!/usr/bin/env python3
"""영어 산출물이 VCMS 용어 정본을 따르는지 검사한다.

정본은 vcms-i18n 의 실제 화면 문자열이다. 사전 번역이 아니라 제품이 쓰는 말이다.
    ~/projects/vcms-i18n/locales/latest/{ko,en}.json

각 규칙은 i18n 키 경로를 근거로 달고 있다. 근거 없는 규칙은 넣지 않는다.

    python3 scripts/glossary_check.py <파일 또는 디렉터리> ...
    python3 scripts/glossary_check.py --rules        # 규칙과 근거만 출력
"""
import json, os, re, sys

I18N = os.path.expanduser("~/projects/vcms-i18n/locales/latest")

# ko 원어 -> 금지 변형들. canon 영어와 근거 키는 i18n 에서 찾아 붙인다.
BAD = {
    "판매 관리": ["sales management", "sales admin", "selling management"],
    "예약": ["reservation"],
    "상품": ["product"],
    "잔여": ["remaining inventory", "remaining stock"],
    "연동 서비스": ["linked service", "linked services", "integrated service", "integrated services"],
    "재고": ["stock"],
    "요금": ["fee", "fees", "charge", "charges", "price plan"],
    "연동일": ["linked date", "sync day"],
    "임시 저장": ["temporary save", "temporarily save", "save temporarily"],
    "화면 보기 설정": ["view filter", "display filter", "screen settings"],
    "일괄 변경": ["bulk change", "batch change"],
    "채널 상품": ["channel product", "channel products"],
    "객실 타입": ["room category", "roomtype "],
    "숙박업소": ["lodging business", "accommodation business"],
    "내보내기": ["export user", "eject"],
    "판매 중지": ["sales stop", "sales closed", "suspend sale", "selling stopped"],
    "대실": ["daytime use", "day-use rental"],
    "숙박": ["overnight stay use"],
}
# 오탐 방지. 근거를 달아둔다. 근거 없이 넓히면 검사기가 무력해진다.
ALLOW = [
    r"rooms? (and|&) rates",            # Expedia/Trip.com 실제 메뉴명
    r"rates? (and|&) restrictions",     # Expedia 실제 메뉴명
    r"business registration",           # 사업자등록번호
    r"https?://",                       # URL 안의 단어는 채널사 경로다
    r"reservation settings",            # 아고다 YCS 실제 메뉴명
    r"sales admin site for motels",     # 야놀자 오너앱 설명. VCMS 판매 관리가 아니다
]
# 요금(Rate) 규칙은 구독 청구 문맥에서 끈다.
# i18n 자신이 그 문맥에 fee/charge 를 쓴다: 오늘 결제 금액 -> "Today's charge", 청구 -> "Billing"
BILLING_CTX = re.compile(
    r"subscription|subscribe|billing|invoice|vat|refund|per room|bundle|payment|paid|"
    r"free trial|notification contact|charged for the addition|before a charge", re.I)
BILLING_RULES = {"요금"}
# 상품(Package) 규칙은 회사 제품을 가리킬 때 끈다.
PRODUCT_ALLOW = re.compile(r"(vendit|another|the|our|this) product\b", re.I)


def canon():
    ko = json.load(open(f"{I18N}/ko.json", encoding="utf-8"))
    en = json.load(open(f"{I18N}/en.json", encoding="utf-8"))

    def flat(d, p=""):
        for k, v in d.items():
            n = f"{p}.{k}" if p else k
            if isinstance(v, dict):
                yield from flat(v, n)
            else:
                yield n, v
    K, E = dict(flat(ko)), dict(flat(en))
    out = {}
    for term in BAD:
        hits = [(k, E[k]) for k, v in K.items() if v == term and k in E]
        if hits:
            out[term] = {"en": hits[0][1], "key": hits[0][0], "n": len(hits)}
    return out


def scan(paths, rules):
    findings = []
    files = []
    for p in paths:
        if os.path.isdir(p):
            for r, _, fs in os.walk(p):
                files += [os.path.join(r, f) for f in fs if f.endswith((".mdx", ".md", ".json", ".txt"))]
        else:
            files.append(p)
    files = [f for f in files if "/reference/" not in f]
    for f in files:
        try:
            lines = open(f, encoding="utf-8").read().splitlines()
        except Exception:
            continue
        for i, line in enumerate(lines, 1):
            low = line.lower()
            if any(re.search(a, low) for a in ALLOW):
                continue
            for term, variants in BAD.items():
                if term not in rules:
                    continue
                if term in BILLING_RULES and ("billing" in f or BILLING_CTX.search(line)):
                    continue
                if term == "상품" and PRODUCT_ALLOW.search(line):
                    continue
                for v in variants:
                    if re.search(r"\b" + re.escape(v), low):
                        findings.append((f, i, v, rules[term]["en"], rules[term]["key"], line.strip()[:90]))
    return findings, len(files)


def main():
    rules = canon()
    if "--rules" in sys.argv:
        print(f"{'ko':14} {'canon en':22} {'i18n 키 경로':52} 키수")
        for t, r in rules.items():
            print(f"{t:14} {r['en']:22} {r['key']:52} {r['n']}")
        missing = [t for t in BAD if t not in rules]
        if missing:
            print("\ni18n 에 정확 일치 키 없음(규칙에서 제외됨):", missing)
        return
    findings, nf = scan(sys.argv[1:], rules)
    for f, i, v, en, key, line in findings:
        print(f"{f}:{i}  '{v}' -> '{en}'   [{key}]\n    {line}")
    print(f"\n검사 파일 {nf}개 | 위반 {len(findings)}건")
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
