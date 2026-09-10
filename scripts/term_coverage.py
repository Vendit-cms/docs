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
            et = norm(open(ep, encoding="utf-8").read())
            for term in present(kt, terms):
                if any(norm(e) and norm(e) in et for e in terms[term]):
                    continue
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
